import logging
from dataclasses import dataclass
from .models import TranslationEndpoint, TranslationSpec, TranslationArtifact
from .excpetions import MultipleActiveSpecs, TranslationException
from .schemas import TranslationSpecDefinitionSchema
from .llm_providers import TogetherAIProvider
from .constants import TranslationArtifcatImplType, EngineOptions


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


class AbstractTranslatorExecutor:

    def __init__(self, context: TranslationContext, spec: TranslationSpec):
        self.context = context
        self.spec = spec

    def run(self) -> TranslatedContext:
        raise NotImplementedError("method must be implemented")


class DynamicTranslatorExecutor(AbstractTranslatorExecutor):

    logger = logging.getLogger(f"llm_translator.{__name__}")
    INVALID_INPUT = "INVALID_INPUT"

    def run(self) -> TranslatedContext:
        self.spec_definition = TranslationSpecDefinitionSchema(**self.spec.definition)

        self.prompt = f"""
            You are a specialized data converter.
            You know how to convert data from {self.spec_definition.input_rule.content_type}
            to {self.spec_definition.output_rule.content_type}.

            You have been given the following input data and schema:
            [INPUT DATA]
            {self.context.body}

            Your task is to convert this data to {self.spec_definition.output_rule.content_type}.
            You must return only the data, not the schema and not any other instructions.
            
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
            translated_content_type = self.spec_definition.output_rule.content_type

        self.logger.info(f"Translation body `{body}`")
        if self.INVALID_INPUT in body:
            message = f"The provided input is not a valid `{self.spec_definition.input_rule.content_type}` content"
            self.logger.error(message)
            raise TranslationException(message)

        return TranslatedContext(
            content_type=translated_content_type,
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
                return {"content": implementation.call(self.prompt), "provider": p}
            except Exception as e:
                self.logger.error(f"Error calling `{p}` LLM: {e}")
                continue


class CompiledArtifactTranslatorExecutor(AbstractTranslatorExecutor):

    logger = logging.getLogger(f"llm_translator.{__name__}")

    def run(self) -> TranslatedContext:

        self.artifact = TranslationArtifact.objects.filter(spec=self.spec).first()

        if not self.artifact:
            message = f"No compiled artifact found for spec {self.spec.name}"
            self.logger.error(message)
            raise TranslationException(message)

        resolvers = {
            TranslationArtifcatImplType.PYTHON: self.__run_python_artifact,
        }

        resolver = resolvers.get(self.artifact.implementation_type)
        if not resolver:
            message = f"Implementation type `{self.artifact.implementation_type}` not supported"
            self.logger.error(message)
            raise TranslationException(message)

        return resolver()

    def __run_python_artifact(self):
        env_locals = {}

        self.logger.info(
            f"Running python compiled artifact: \n{self.artifact.implementation_str}"
        )

        self.logger.info(f"{self.context.body}")

        exec(self.artifact.implementation_str, {}, env_locals)
        translate = env_locals.get("translate")

        if not translate:
            message = f"Invalid compiled artifact: did not find `translate` function"
            self.logger.error(message)
            raise TranslationException(message)

        translated = translate(
            {"data": self.context.body, "content_type": self.context.content_type}
        )

        return TranslatedContext(
            content_type=self.spec.definition["output_rule"]["content_type"],
            body=translated,
            provider=EngineOptions.COMPILED_ARTIFACT,
        )


class TranslatorService:

    logger = logging.getLogger(f"llm_translator.{__name__}")

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

        # 2. Execute Translator
        executor = self.__get_executor()

        try:
            return executor.run()
        except Exception as e:
            import traceback

            traceback.print_exc()
            self.logger.error(f"Error translating content: {e}")
            raise TranslationException(str(e))

    def __get_executor(self):
        if self.spec.definition["engine"] == "dynamic":
            return DynamicTranslatorExecutor(self.context, self.spec)
        elif self.spec.definition["engine"] == "compiled_artifact":
            return CompiledArtifactTranslatorExecutor(self.context, self.spec)
        else:
            raise TranslationException(
                f"Invalid engine `{self.spec.definition['engine']}`"
            )
