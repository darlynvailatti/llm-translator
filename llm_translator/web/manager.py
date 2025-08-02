import traceback
import uuid
from typing import Optional
import logging
from datetime import datetime
from dataclasses import dataclass
from .constants import TranslationTestCaseStatus, EngineOptions
from .models import (
    TranslationEndpoint,
    TranslationEvent,
    TranslationEventStatus,
    TranslationArtifact,
    TranslationSpec,
    SpecTestCase,
    SpecTestCaseExecution,
)
from .translator.service import TranslatorService
from .translator.models import TranslationContext
from .translator.executors import CompiledArtifactTranslatorExecutor
from .translator.artifact import TranslationArtifactGenerator
from .schemas import SpecTestCaseDefinitionSchema, TranslationSpecDefinitionSchema
from .excpetions import ArtifcatGenerationException


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
    it_generated_artifact: bool
    it_passed_all_test_cases: bool
    failed_test_cases: Optional[list[SpecTestCase]] = None
    message: Optional[str] = None
    stacktrace: Optional[str] = None
    artifact: Optional[TranslationArtifact] = None


class ArtifactGeneratorManager:

    logger = logging.getLogger(f"llm_translator.{__name__}")

    def handle(self, request: ArtifactGenerationRequest) -> ArtifactGenerationResponse:
        try:
            spec = TranslationSpec.objects.get(uuid=request.spec_id)
            spec_test_cases = SpecTestCase.objects.filter(spec=spec)
            artifact = TranslationArtifact.objects.filter(spec=spec).first()

            try:
                latest_test_case = spec_test_cases.latest("updated_at")
            except SpecTestCase.DoesNotExist:
                raise ArtifcatGenerationException(
                    "At least one test case must be created!"
                )

            self.logger.info(
                f"Latest test case updated at: {latest_test_case.updated_at}"
            )
            self.logger.info(
                f"Artifact updated at: {artifact.updated_at if artifact else None}"
            )

            artifact_is_outdated = (
                artifact and latest_test_case.updated_at > artifact.updated_at
            )

            try:
                if not artifact or artifact_is_outdated:
                    self.logger.info(
                        "No artificat found or outdated, generating new artifact"
                    )
                    artifact = TranslationArtifactGenerator(spec).generate()
            except Exception as e:
                raise ArtifcatGenerationException(f"Error generating artifact: {e}")

            if not artifact:
                raise ArtifcatGenerationException(
                    f"No artifact found for spec {spec.name}"
                )
            
            exec_response = SpecTestCaseExecutor(spec).run_all()
            executions = exec_response.executions
            failed_test_cases = [
                exec.test_case
                for exec in executions
                if exec.status == TranslationTestCaseStatus.FAILURE
            ]
            it_passed_all_test_cases = exec_response.success

            return ArtifactGenerationResponse(
                success=True,
                it_generated_artifact=artifact is not None,
                it_passed_all_test_cases=it_passed_all_test_cases,
                failed_test_cases=failed_test_cases,
                message=None,
                artifact=artifact,
            )
        except ArtifcatGenerationException as e:
            stacktrace = traceback.format_exc()
            msg = f"Error generating artifact: {e}"
            self.logger.error(msg, exc_info=True)
            return ArtifactGenerationResponse(
                success=False,
                it_generated_artifact=False,
                it_passed_all_test_cases=False,
                message=msg,
                stacktrace=stacktrace,
                artifact=None,
            )
        except Exception as e:
            stacktrace = traceback.format_exc()
            msg = f"Error generating artifact: {e}"
            self.logger.error(msg, exc_info=True)
            return ArtifactGenerationResponse(
                success=False,
                it_generated_artifact=False,
                it_passed_all_test_cases=False,
                message=msg,
                stacktrace=stacktrace,
                artifact=None,
            )


@dataclass
class SpecTestCaseExecutionResponse:
    success: bool
    executions: list[SpecTestCaseExecution]


class SpecTestCaseExecutor:

    logger = logging.getLogger(f"llm_translator.{__name__}")

    def __init__(self, spec: TranslationSpec):
        self.spec = spec
        self.spec_def = TranslationSpecDefinitionSchema(**spec.definition)

        if self.spec_def.engine != EngineOptions.COMPILED_ARTIFACT:
            raise ValueError(
                "SpecTestCaseExecutor only supported for specs with compiled artifacts"
            )

    def run_all(self) -> SpecTestCaseExecutionResponse:
        self.test_cases = SpecTestCase.objects.filter(spec=self.spec)
        is_success = True
        executions = []
        for tc in self.test_cases:
            execution = self.__run_test_case(tc)
            if execution.status != TranslationTestCaseStatus.SUCCESS:
                is_success = False
            executions.append(execution)

        return SpecTestCaseExecutionResponse(
            success=is_success,
            executions=executions,
        )

    def run(self, test_case: SpecTestCase) -> SpecTestCaseExecutionResponse:
        execution = self.__run_test_case(test_case)
        return SpecTestCaseExecutionResponse(
            success=execution.status == TranslationTestCaseStatus.SUCCESS,
            executions=[test_case],
        )

    def __run_test_case(self, test_case: SpecTestCase) -> SpecTestCaseExecution:
        test_spec_def = SpecTestCaseDefinitionSchema(**test_case.definition)
        execution = SpecTestCaseExecution(
            test_case=test_case, executed_at=datetime.now().isoformat()
        )
        try:
            self.logger.info(f"Running test case `{test_case.name}`")
            tc_definition = SpecTestCaseDefinitionSchema(**test_case.definition)
            context = TranslationContext(
                endpoint=self.spec.endpoint,
                content_type=self.spec_def.input_rule.content_type,
                body=tc_definition.input.body.encode(),
            )
            translated = CompiledArtifactTranslatorExecutor(context, self.spec).run()

            # Is translated body equals to test case's expected?
            status = TranslationTestCaseStatus.SUCCESS
            message = "Success"
            # Compare content by converting both to strings
            translated_body_str = translated.body.decode()
            if translated_body_str != tc_definition.expectation.body:
                self.logger.error(f"Translated payload is different from expected")
                status = TranslationTestCaseStatus.FAILURE
                message = "Translated payload is different from expected"

            self.logger.info(f"Test case `{test_case.name}` ran, status is: {status}")
            execution.status = status
            execution.result = {
                "message": message,
                "translated": {
                    "content_type": translated.content_type,
                    "body": translated.body.decode(),
                },
                "expectation": {
                    "body": tc_definition.expectation.body,
                },
            }
        except Exception as e:
            stacktrace = traceback.format_exc()
            msg = f"Unkown error: {e}\n{stacktrace}"
            self.logger.error(f"Error running test case `{test_case.name}`: {msg}")
            execution.status = TranslationTestCaseStatus.FAILURE
            execution.result = {
                "message": msg,
            }
        finally:

            # If the test case is expected to fail, it should be considered a success
            if test_spec_def.expectation.result != execution.status:
                msg = f"Test case is expected for `{test_spec_def.expectation.result}` but resulted in `{execution.status}`"
                self.logger.info(msg)
                execution.status = TranslationTestCaseStatus.FAILURE
                execution.result = {
                    **execution.result,
                    "message": f"{msg}. Original message was: {execution.result['message']}",
                }

            execution.save()
        
        return execution
