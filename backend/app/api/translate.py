from fastapi import APIRouter, status
from app.schemas.translation import TranslationRequest, TranslationResponse
from app.services.translation_service import TranslationService

router = APIRouter(prefix="/api/translate", tags=["Translation"])


@router.post(
    "",
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Translate dynamic content",
    description="Translate dynamic text strings into target language (Hindi, Nagpuri, Santali) using Gemini with graceful fallback.",
)
def translate_content(payload: TranslationRequest):
    translated = TranslationService.translate_texts(
        texts=payload.texts,
        target_language=payload.target_language,
        source_language=payload.source_language or "en",
    )
    return TranslationResponse(
        translations=translated,
        target_language=payload.target_language,
        source_language=payload.source_language or "en",
    )
