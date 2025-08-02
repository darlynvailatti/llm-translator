import logging
from ..models import TranslationSpec
from ..excpetions import MultipleActiveSpecs, TranslationException
from .models import TranslationContext, TranslatedContext
from .executors import (
    DynamicTranslatorExecutor,
    CompiledArtifactTranslatorExecutor,
)

class TranslatorService:
    logger = logging.getLogger(f"llm_translator.{__name__}")
    def __init__(self, context: TranslationContext):
        self.context = context
    def translate(self) -> TranslatedContext:
        self.logger.info(
            f"Translating content for endpoint {self.context.endpoint.uuid}"
        )
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