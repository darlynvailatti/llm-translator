import logging
from .models import TranslationContext, TranslatedContext
from ..constants import TranslationArtifcatImplType, EngineOptions
from ..llm.dspy_interfaces import TranslationPromptModule
from ..models import TranslationSpec, TranslationArtifact
from ..excpetions import TranslationException
from ..schemas import TranslationSpecDefinitionSchema

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
        self.logger.info(
            f"Using TranslationSpecification: `{self.spec.name}` version `{self.spec.version}`"
        )
        
        try:
            prompt_module = TranslationPromptModule()
            translated = prompt_module.forward(
                input_type=self.spec_definition.input_rule.content_type,
                output_type=self.spec_definition.output_rule.content_type,
                input_data=self.context.body,
                extra_instructions=self.spec_definition.extra_context,
            )
            self.logger.info(f"Prompt result: {translated}")
        except Exception as e:
            self.logger.error(f"Error in prompt_module.forward: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
    

        body = ""
        provider = None
        message = None
        if not translated:
            message = "No LLM provider was able to translate the content"
            self.logger.error(message)
            raise TranslationException(message)
        else:
            body = translated
            provider = "dspy"
            translated_content_type = self.spec_definition.output_rule.content_type

        return TranslatedContext(
            content_type=translated_content_type,
            body=body,
            provider=provider,
        )

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
        
        self.logger.info(f"Input data: {type(self.context.body)})")
        translated = translate(self.context.body)
        return TranslatedContext(
            content_type=self.spec.definition["output_rule"]["content_type"],
            body=translated,
            provider=EngineOptions.COMPILED_ARTIFACT,
        ) 