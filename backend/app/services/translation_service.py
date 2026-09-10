import importlib
import json
import logging
from typing import Any, List, Optional

from app.core.config import settings
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

LANGUAGE_PROFILES = {
    "hi": "Hindi (written naturally in clean Devanagari script)",
    "nag": "Nagpuri / Sadri (a prominent regional language of Jharkhand, written in Devanagari script with natural colloquial regional phrasing)",
    "sat": "Santali (the major tribal language of Jharkhand, written in Ol Chiki script or natural Santali)",
    "en": "English",
}


class TranslationService:
    @classmethod
    def translate_texts(
        cls,
        texts: List[str],
        target_language: str,
        source_language: str = "en",
        client: Optional[Any] = None,
    ) -> List[str]:
        """Translate a batch of text strings into the target language using Gemini.
        Preserves original text if target is English or if translation fails.
        """
        if not texts:
            return []

        target_lang = target_language.lower().strip()
        if target_lang == "en" or target_lang == source_language.lower().strip():
            return texts

        # Filter out empty or whitespace-only strings
        non_empty_pairs = [(idx, t.strip()) for idx, t in enumerate(texts) if isinstance(t, str) and t.strip()]
        if not non_empty_pairs:
            return texts

        non_empty_indices = [idx for idx, _ in non_empty_pairs]
        non_empty_texts = [t for _, t in non_empty_pairs]

        lang_desc = LANGUAGE_PROFILES.get(target_lang, target_lang)

        prompt = (
            f"You are an expert civic-tech translator for SolveSphere in Jharkhand, India.\n"
            f"Translate the following JSON array of text strings from {source_language} into {lang_desc}.\n\n"
            "Critical Translation Rules:\n"
            "1. DO NOT translate proper nouns: Person names, Institution names (e.g., 'Jharkhand Water Research Institute', 'BIT Mesra'), District names (e.g., 'Ranchi', 'Dhanbad', 'Hazaribagh'), or State name ('Jharkhand').\n"
            "2. DO NOT translate numbers, dates, metrics, percentages, or technical IDs (e.g., '1000', '8.5', '2026-09-08').\n"
            "3. For Nagpuri, use authentic Jharkhandi Sadri/Nagpuri vocabulary and phrasing in Devanagari script.\n"
            "4. For Santali, use Ol Chiki script or authentic Santali vocabulary.\n"
            "5. For Hindi, produce high-quality, natural civic phrasing in Devanagari script.\n"
            "6. Return ONLY a valid JSON array of translated strings in the EXACT same order and length as the input array.\n\n"
            f"Input JSON Array:\n{json.dumps(non_empty_texts, ensure_ascii=False)}"
        )

        try:
            active_client = client or GeminiService.get_client()
            genai_types = importlib.import_module("google.genai.types")
            config = genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
                automatic_function_calling=genai_types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            )
            response = active_client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
            raw_text = getattr(response, "text", "")
            if raw_text:
                parsed = json.loads(raw_text)
                trans_items = None
                if isinstance(parsed, list):
                    trans_items = parsed
                elif isinstance(parsed, dict):
                    for key in ["translations", "translated_texts", "result", "items"]:
                        if key in parsed and isinstance(parsed[key], list):
                            trans_items = parsed[key]
                            break

                if trans_items and len(trans_items) == len(non_empty_texts):
                    result = list(texts)
                    for i, orig_idx in enumerate(non_empty_indices):
                        translated_val = trans_items[i]
                        if isinstance(translated_val, str) and translated_val.strip():
                            result[orig_idx] = translated_val.strip()
                    return result
        except Exception as e:
            logger.warning(f"Translation failed for language '{target_language}': {e}")

        # Graceful fallback: return original text intact
        return texts
