from typing import Optional
import logging
import uuid
from datetime import datetime
from dataclasses import dataclass
from .constants import TranslationTestCaseStatus
from .models import (
    TranslationEndpoint,
    TranslationEvent,
    TranslationEventStatus,
    TranslationArtifact,
    TranslationSpec,
    SpecTestCase
)
from .translator import TranslatorService, TranslationContext, CompiledArtifactTranslatorExecutor
from .artifact import TranslationArtifactGenerator
from .schemas import SpecTestCaseDefinitionSchema, TranslationSpecDefinitionSchema


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
                body=translated.body,
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
                    "body": request.body.decode(),
                },
            }

            if translated:
                ctx.update(
                    {
                        "translated": {
                            "content_type": translated.content_type,
                            "body": str(translated.body),
                            "provider": translated.provider,
                        }
                    }
                )

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


@dataclass
class ArtifactGenerationRequest:
    spec_id: str


@dataclass
class ArtifactGenerationResponse:
    success: bool
    message: Optional[str]
    artifact: Optional[TranslationArtifact]


class ArtifactGeneratorManager:

    logger = logging.getLogger(f"llm_translator.{__name__}")

    def handle(self, request: ArtifactGenerationRequest) -> ArtifactGenerationResponse:
        try:
            spec = TranslationSpec.objects.get(uuid=request.spec_id)
            spec_def = TranslationSpecDefinitionSchema(**spec.definition)
            spec_test_cases = SpecTestCase.objects.filter(spec=spec)

            artifact = TranslationArtifact.objects.filter(spec=spec).first()
            latest_test_case = spec_test_cases.latest("updated_at")

            self.logger.info(f"Latest test case updated at: {latest_test_case.updated_at}")
            self.logger.info(f"Artifact updated at: {artifact.updated_at if artifact else None}")

            artifact_is_outdated = (artifact and latest_test_case.updated_at > artifact.updated_at)

            if not artifact or artifact_is_outdated:
                self.logger.info("No artificat found or outdated, generating new artifact")
                artifact = TranslationArtifactGenerator(spec).generate()

            if not artifact:
                raise Exception(f"No artifact found for spec {spec.name}")

            # Run test cases for the generated artifact
            for tc in spec_test_cases:

                self.logger.info(f"Running test case `{tc.name}`")
                tc_definition = SpecTestCaseDefinitionSchema(**tc.definition)
                context = TranslationContext(
                    endpoint=spec.endpoint,
                    content_type=spec_def.input_rule.content_type,
                    body=tc_definition.input.body
                )
                translated = CompiledArtifactTranslatorExecutor(
                    context, spec
                ).run()

                # Is translated body equals to test case's expected?
                if translated.body == tc_definition.expectation.body:
                    tc.status = TranslationTestCaseStatus.SUCCESS
                else:
                    tc.status = TranslationTestCaseStatus.FAILURE

                self.logger.info(f"Test case `{tc.name}` status: {tc.status}")

                tc.executed_at = datetime.now()
                tc.save()

            return ArtifactGenerationResponse(success=True, message=None, artifact=artifact)
        except Exception as e:
            self.logger.error(f"Error generating artifact: {e}")
            return ArtifactGenerationResponse(success=False, message=str(e), artifact=None)
        
        
