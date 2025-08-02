from dataclasses import dataclass
from ..models import TranslationEndpoint, TranslationSpec

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