import logging
import uuid
from datetime import datetime
from dataclasses import dataclass
from .models import TranslationEndpoint, TranslationEvent, TranslationEventStatus
from .translator import TranslatorService, TranslationContext


@dataclass
class TranslationRequest:
    content_type: str
    body: bytes
    endpoint_id: str


@dataclass
class TranslationResponse:
    success: bool
    message: str
    content_type: str
    body: bytes
    duration: float


class TranslationManager:

    logger = logging.getLogger(f"llm_translator.{__name__}")

    def handle(self, request: TranslationRequest) -> TranslationResponse:
        self.logger.info(f"Handling request for endpoint {request.endpoint_id}")
        start_at = datetime.now()
        time_taken = 0
        status = TranslationEventStatus.SUCCESS
        endpoint = self.__find_endpoint(request.endpoint_id)
        translated = None

        if not endpoint:
            msg = f"Endpoint {request.endpoint_id} not found"
            self.logger.error(msg)
            status = TranslationEventStatus.FAILURE
            return TranslationResponse(
                success=False,
                message=msg,
                content_type=None,
                body=bytes(),
                duration=time_taken,
            )

        try:
            context = TranslationContext(
                endpoint=endpoint, content_type=request.content_type, body=request.body
            )
            translated = TranslatorService(context).translate()

            time_taken = (datetime.now() - start_at).total_seconds()
            status = TranslationEventStatus.SUCCESS

            response = TranslationResponse(
                content_type=translated.content_type,
                body=str(translated.body).encode(),
                duration=time_taken,
                success=True,
                message="Success",
            )
        except Exception as e:
            time_taken = (datetime.now() - start_at).total_seconds()
            msg = f"Error handling translation request: {e}"
            self.logger.error(msg)
            status = TranslationEventStatus.FAILURE
            response = TranslationResponse(
                success=False,
                message=msg,
                content_type=None,
                body=bytes(),
                duration=time_taken,
            )
        finally:
            self.logger.info(f"Request handled in {time_taken} seconds")

            ctx = {
                "duration": time_taken,
                "request": {
                    "content_type": request.content_type,
                    "body": request.body,
                }
            }

            if translated:
                ctx.update({"translated": {
                    "content_type": translated.content_type,
                    "body": translated.body,
                    "provider": translated.provider
                }})

            TranslationEvent.objects.create(
                status=status, context=ctx, endpoint=endpoint
            )
            return response

    def __find_endpoint(self, endpoint_id: str) -> TranslationEndpoint:
        try:
            uuid.UUID(endpoint_id)
            return TranslationEndpoint.objects.get(uuid=endpoint_id)
        except (ValueError, TranslationEndpoint.DoesNotExist):
            try:
                return TranslationEndpoint.objects.get(key=endpoint_id)
            except TranslationEndpoint.DoesNotExist:
                return None
