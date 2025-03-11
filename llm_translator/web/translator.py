import logging
from dataclasses import dataclass
from .models import TranslationEndpoint, TranslationSpec
from .excpetions import MultipleActiveSpecs, TranslationException
from .schemas import TranslationSpecDefinitionSchema
from .llm_providers import TogetherAIProvider


@dataclass
class TranslationContext:
    endpoint: TranslationEndpoint
    content_type: str
    body: bytes


@dataclass
class TranslatedContext:
    content_type: str
    body: bytes
    provider: str


class TranslatorService:

    logger = logging.getLogger(f"llm_translator.{__name__}")
    INVALID_INPUT = "INVALID_INPUT"

    def __init__(self, context: TranslationContext):
        self.context = context

    def translate(self) -> TranslatedContext:
        self.logger.info(
            f"Translating content for endpoint {self.context.endpoint.uuid}"
        )

        # 1. Get TranslationSpecifictation
        specs = TranslationSpec.objects.filter(
            endpoint=self.context.endpoint, is_active=True
        )

        if specs.count() > 1:
            msg = f"Multiple active TranslationSpecifications found for endpoint {self.context.endpoint.uuid}"
            self.logger.error(msg)
            raise MultipleActiveSpecs(msg)

        if not specs.exists():
            msg = f"No active TranslationSpecifications found for endpoint {self.context.endpoint.uuid}"
            self.logger.error(msg)
            raise TranslationException(msg)

        self.spec = specs.first()
        self.spec_definition = TranslationSpecDefinitionSchema(**self.spec.definition)

        self.prompt = f"""
            You are a specialized data converter.
            You know how to convert data from {self.spec_definition.input_rule.content_type}
            to {self.spec_definition.output_rule.content_type}.

            You have been given the following input data and schema:
            [INPUT DATA]
            {self.context.body}

            Your task is to convert this data to {self.spec_definition.output_rule.content_type}.
            You must return ONLY the raw data, not the schema, AND not any other instructions, information or formatting.
            If the input data is not a valid {self.spec_definition.input_rule.content_type}, you must return "INVALID_INPUT".
            
            You must also adhere to the following extra instructions:
            [EXTRA INSTRUCTIONS]
            {self.spec_definition.extra_context}


        """

        self.logger.info(
            f"Using TranslationSpecification: `{self.spec.name}` version `{self.spec.version}`"
        )

        self.logger.info(f"Prompting LLMs with: {self.prompt}")
        translated = self.__call_llm()

        body = ""
        provider = None
        message = None

        if not translated or not translated["content"]:
            message = "No LLM provider was able to translate the content"
            self.logger.error(message)
            raise TranslationException(message)
        else:
            body = translated["content"]
            provider = translated["provider"]

        self.logger.info(f"Translation body `{body}`")
        if self.INVALID_INPUT in body:
            message = f"The provided input is not a valid `{self.spec_definition.input_rule.content_type}` content"
            self.logger.error(message)
            raise TranslationException(message)

        return TranslatedContext(
            content_type=self.context.content_type,
            body=body,
            provider=provider,
        )

    def __call_llm(self):

        llm_providers = {
            # "ollama": OllamaLocalAPIProvider(),
            "together": TogetherAIProvider()
        }
        


        for p, implementation in llm_providers.items():
            try:
                self.logger.info(f"Calling `{p}` LLM")
                return { "content": implementation.call(self.prompt), "provider": p }
            except Exception as e:
                self.logger.error(f"Error calling `{p}` LLM: {e}")
                continue
            
