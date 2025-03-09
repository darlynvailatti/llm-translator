from typing import Optional
from pydantic import BaseModel

class InputSpecRule(BaseModel):
    content_type: str
    schema_: Optional[str] = None

class OutputSpecRule(BaseModel):
    content_type: str
    schema_: Optional[str] = None

class TranslationSpecDefinitionSchema(BaseModel):
    input_rule: Optional[InputSpecRule]
    output_rule: Optional[OutputSpecRule]
    extra_context: Optional[str]