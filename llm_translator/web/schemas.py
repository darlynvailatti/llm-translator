from typing import Optional
from pydantic import BaseModel, Field
from .constants import EngineOptions, ExpectationResult
class InputSpecRule(BaseModel):
    content_type: str
    schema_: Optional[str] = None

class OutputSpecRule(BaseModel):
    content_type: str
    schema_: Optional[str] = None

class TranslationSpecDefinitionSchema(BaseModel):
    engine: EngineOptions = Field(default=EngineOptions.DYNAMIC, description="The engine that will be used to translate the data")
    input_rule: Optional[InputSpecRule]
    output_rule: Optional[OutputSpecRule]
    extra_context: Optional[str]

class SpecTestCaseInputDefinitionSchema(BaseModel):
    body: str

class SpecTestCaseExpectationDefinitionSchema(BaseModel):
    body: str
    result: ExpectationResult = Field(default=ExpectationResult.SUCESS, description="The expected result of the test case")

class SpecTestCaseDefinitionSchema(BaseModel):
    input: SpecTestCaseInputDefinitionSchema
    expectation: SpecTestCaseExpectationDefinitionSchema

class SpecTestCaseSchema(BaseModel):
    name: str
    definition: SpecTestCaseDefinitionSchema 