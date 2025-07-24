import re
import logging
from .models import TranslationSpec, TranslationArtifact, SpecTestCase
from .excpetions import ArtifcatGenerationException
from .schemas import TranslationSpecDefinitionSchema, SpecTestCaseDefinitionSchema
from .llm_providers import LLMCaller


class AbstractArtifactGenerator:
    def __init__(self, spec: TranslationSpec):
        self.spec = spec

    def generate(self) -> TranslationArtifact:
        raise NotImplementedError("generate() method must be implemented")


class TranslationArtifactGenerator(AbstractArtifactGenerator):

    logger = logging.getLogger(f"llm_translator.{__name__}")

    def generate(self) -> TranslationArtifact:

        try:
            self.test_cases = SpecTestCase.objects.filter(spec=self.spec).all()

            if len(self.test_cases) == 0:
                raise Exception("No test cases found for spec")

            self.spec_definition = TranslationSpecDefinitionSchema(
                **self.spec.definition
            )
            self.prompt = self.__get_prompt()

            self.logger.info(f"Prompt: {self.prompt}")

            llm_response = LLMCaller.call(self.prompt)

            sanitized_response = re.sub(r'(```python.*|.*```)', '', llm_response["content"])

            artifact = TranslationArtifact.objects.filter(spec=self.spec).first()
            if not artifact:
                artifact = TranslationArtifact.objects.create(
                    spec=self.spec,
                    implementation=sanitized_response.encode("utf-8"),
                )
            else:
                artifact.implementation = sanitized_response.encode("utf-8")
                artifact.save()
            return artifact
        except Exception as e:
            raise ArtifcatGenerationException(
                f"Failed to generate artifact for spec {self.spec.name}: {e}"
            ) from e

    def __get_prompt(self):

        input_samples = ""
        for tc in self.test_cases:
            tc_def = SpecTestCaseDefinitionSchema(**tc.definition)
            input_samples += f"""
                [INPUT]
                {tc_def.input.body}

                [EXPECTED]
                {tc_def.expectation.body}
            \n\n
            """

        return f"""
            You are an expert data converter specializing in Python. 
            Your task is to generate a Python implementation that converts 
            data from {self.spec_definition.input_rule.content_type} to {self.spec_definition.output_rule.content_type}.

            #### Input Data Sample
            You have been provided with the following sample input and expectation data:
            {input_samples}

            #### Requirements
            - Return **only** plain Python code, without markdown syntax, syntax highlighting, explanations or tripple brackets.
            - **Library Constraints:** You **must use only Python’s built-in or allowed libraries** and import them inside "translate" function. 
                External libraries, services, resources, tools, or frameworks are strictly prohibited.
            - **Allowed Libraries:** You are allowed to use the following libraries:
                •	pyyaml
            - **Code Template:** Your implementation **must** follow the structure below:

            def translate(context) -> bytes:
                \"\"\"
                Converts the input data into the required output format.
                
                :param context: dict containing the key "data" with the input bytes.
                :return: Converted data as bytes.
                \"\"\"

                # >>>>>> Import necessary libraries here

                # >>>>>> Your implementation here
                pass

            Context Parameter
                •	context: A dictionary containing:
                •	"data": A bytes object representing the input data.

            [Additional Instructions]
            You must also adhere to the following extra instructions:
            {self.spec_definition.extra_context}
        """
