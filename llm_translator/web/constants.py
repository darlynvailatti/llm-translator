from enum import Enum

class EngineOptions(str, Enum):
    DYNAMIC = "dynamic"
    COMPILED_ARTIFACT = "compiled_artifact"

class ExpectationResult(str, Enum):
    SUCESS = "success"
    FAILURE = "failure"

class TranslationEventStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

class TranslationTestCaseStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    NOT_EXECUTED = "NOT_EXECUTED"

class TranslationArtifcatImplType(str, Enum):
    PYTHON = "python"