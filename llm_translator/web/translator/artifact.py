import re
import logging
from ..models import TranslationSpec, TranslationArtifact, SpecTestCase
from ..excpetions import ArtifcatGenerationException
from ..schemas import TranslationSpecDefinitionSchema, SpecTestCaseDefinitionSchema
from ..llm.dspy_interfaces import ArtifactGenerationPromptModule


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

            # Build input_samples string
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

            # Use DSPy ArtifactGenerationPromptModule
            prompt_module = ArtifactGenerationPromptModule()
            llm_response = prompt_module.forward(
                input_type=self.spec_definition.input_rule.content_type,
                output_type=self.spec_definition.output_rule.content_type,
                input_samples=input_samples,
                extra_instructions=self.spec_definition.extra_context,
            )

            sanitized_response = re.sub(r"(```python.*|.*```)", "", llm_response)

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
