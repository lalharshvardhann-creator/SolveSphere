from typing import List, Optional
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, description="List of text strings to translate")
    target_language: str = Field(..., min_length=2, max_length=10, description="Target language code (e.g., 'hi', 'or', 'nag', 'sat')")
    source_language: Optional[str] = Field("en", description="Source language code")


class TranslationResponse(BaseModel):
    translations: List[str] = Field(..., description="List of translated strings corresponding to input texts")
    target_language: str
    source_language: str
