import dspy
import requests
import logging
import re


class TranslationSignature(dspy.Signature):
    """You are a data conversion expert. Convert the input data from {input_type} to {output_type}."""

    input_type: str = dspy.InputField(
        desc="The type of the input data (e.g., JSON, XML, etc.)"
    )
    output_type: str = dspy.InputField(
        desc="The type to convert the data to (e.g., XML, JSON, etc.)"
    )
    input_data: str = dspy.InputField(desc="The actual data to convert.")
    extra_instructions: str = dspy.InputField(
        desc="Any extra instructions for the conversion."
    )
    output: str = dspy.OutputField(
        desc="The converted data, with no extra text or schema."
    )


class TranslationPromptModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(TranslationSignature)
        self.logger = logging.getLogger(f"{__name__}.TranslationPromptModule")

    def forward(self, input_type, output_type, input_data, extra_instructions=None):
        try:
            result = self.predict(
                input_type=input_type,
                output_type=output_type,
                input_data=input_data,
                extra_instructions=extra_instructions or "",
            )
            self.logger.info(f"Predict result: {result}")
            self.logger.info(f"Predict result type: {type(result)}")
            self.logger.info(f"Predict result attributes: {dir(result)}")
            
            output = result.output
            self.logger.info(f"Extracted output: {repr(output)}")
            
            return output
        except Exception as e:
            self.logger.error(f"Error in predict: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise


class ArtifactGenerationSignature(dspy.Signature):
    """You are an expert data translator specializing in Python. Generate a
    Python function that translates data from {input_type} to {output_type} 
    using the provided samples and instructions as reference.

    CRITICAL REQUIREMENTS:
    1. Return ONLY the Python function code, no explanations, no markdown, no comments outside the function
    2. The function must be named `translate` and take a single parameter `data` as bytes object
    3. The function must return a `bytes` object
    4. Do not include any text before or after the function definition
    5. Do not include ```python or ``` markers
    6. Do not include any explanatory text

    Example of a valid function implementation:
    def translate(data: bytes) -> bytes:
        # Your code here
        # translated = ...
        return translated

    IMPORTANT: Return ONLY the function code starting with 'def translate' and ending with the return statement.
    """

    input_type: str = dspy.InputField(
        desc="The type of the input data (e.g., JSON, XML, etc.)"
    )
    output_type: str = dspy.InputField(
        desc="The type to convert the data to (e.g., XML, JSON, etc.)"
    )
    input_samples: str = dspy.InputField(
        desc="Sample input and expected output pairs for the conversion task."
    )
    extra_instructions: str = dspy.InputField(
        desc="Any extra instructions or requirements for the implementation."
    )
    output: str = dspy.OutputField(
        desc="The generated Python function code as a string, with no extra text, markdown, or explanations."
    )


class ArtifactGenerationPromptModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ArtifactGenerationSignature)
        self.logger = logging.getLogger(f"{__name__}.ArtifactGenerationPromptModule")

    def _clean_python_code(self, code: str) -> str:
        """Clean the generated Python code to extract only the function."""
        if not code:
            return ""
        
        # Remove markdown code blocks
        code = re.sub(r'```python\s*', '', code)
        code = re.sub(r'```\s*$', '', code)
        code = re.sub(r'```\s*', '', code)
        
        # Remove leading/trailing whitespace
        code = code.strip()
        
        # Find the function definition
        lines = code.split('\n')
        start_idx = None
        end_idx = None
        
        # Find the start of the function (def translate)
        for i, line in enumerate(lines):
            if line.strip().startswith('def translate'):
                start_idx = i
                break
        
        if start_idx is None:
            self.logger.warning("No 'def translate' found in generated code")
            return code
        
        # Find the end of the function (look for the last return statement or end of indented block)
        in_function = False
        for i, line in enumerate(lines[start_idx:], start_idx):
            stripped = line.strip()
            
            if i == start_idx:
                in_function = True
                continue
            
            if in_function:
                # If we hit a non-indented line that's not empty, we're out of the function
                if stripped and not line.startswith(' ') and not line.startswith('\t'):
                    end_idx = i
                    break
                
                # If we find a return statement, this might be the end
                if stripped.startswith('return '):
                    end_idx = i + 1
        
        if end_idx is None:
            end_idx = len(lines)
        
        # Extract the function
        function_lines = lines[start_idx:end_idx]
        cleaned_code = '\n'.join(function_lines)
        
        self.logger.info(f"Cleaned code length: {len(cleaned_code)}")
        self.logger.debug(f"Cleaned code: {repr(cleaned_code)}")
        
        return cleaned_code

    def forward(self, input_type, output_type, input_samples, extra_instructions=None):
        try:
            result = self.predict(
                input_type=input_type,
                output_type=output_type,
                input_samples=input_samples,
                extra_instructions=extra_instructions or "",
            )
            
            raw_output = result.output
            self.logger.info(f"Raw output length: {len(raw_output)}")
            self.logger.debug(f"Raw output: {repr(raw_output)}")
            
            # Clean the output to extract only the Python function
            cleaned_output = self._clean_python_code(raw_output)
            
            if not cleaned_output:
                raise ValueError("Failed to extract valid Python function from LLM output")
            
            return cleaned_output
            
        except Exception as e:
            self.logger.error(f"Error in artifact generation: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
