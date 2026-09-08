from typing import Optional
from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.ai_analysis import ChallengeAIAnalysisStructured


class GeminiConfigurationError(Exception):
    """Raised when the Gemini API key is missing or misconfigured."""
    pass


class GeminiAPIError(Exception):
    """Raised when communication with the Gemini API fails."""
    pass


class GeminiValidationError(Exception):
    """Raised when the Gemini model output cannot be parsed or validated."""
    pass


class GeminiService:
    @classmethod
    def get_client(cls) -> genai.Client:
        """Create and return an initialized Gemini client using configured API key."""
        api_key = settings.GEMINI_API_KEY
        if not api_key or not api_key.strip():
            raise GeminiConfigurationError(
                "GEMINI_API_KEY is not configured in environment or settings."
            )
        return genai.Client(api_key=api_key.strip())

    @classmethod
    def build_prompt(
        cls,
        title: str,
        description: str,
        category: Optional[str] = None,
        district: Optional[str] = None,
        people_affected: Optional[int] = None,
    ) -> str:
        """Construct a focused system and context prompt for analyzing a SolveSphere societal challenge."""
        prompt = (
            "You are an expert AI analysis engine for SolveSphere, an innovation platform in Jharkhand, India, "
            "that connects local societal challenges with Higher Education Institutions (HEIs), researchers, and industry partners.\n\n"
            "Analyze the following societal challenge and produce a strictly structured JSON response:\n\n"
            f"Challenge Title: {title}\n"
            f"Description: {description}\n"
            f"Submitted Category: {category or 'Not specified'}\n"
            f"District (Jharkhand): {district or 'Not specified'}\n"
            f"Estimated People Affected: {people_affected if people_affected is not None else 'Not specified'}\n\n"
            "Analysis Guidelines:\n"
            "1. problem_summary: A concise 1-2 sentence executive summary of the core issue.\n"
            "2. detected_category: The primary societal/technical domain (e.g., Water Supply, Healthcare, Sanitation, Agriculture, Infrastructure, Education, Clean Energy, Environment).\n"
            "3. detected_subcategory: A more specific sub-topic or domain.\n"
            "4. priority_score: A numerical rating between 1.0 (low urgency) and 10.0 (critical urgency), considering health/safety impact and population affected.\n"
            "5. relevant_keywords: A list of 4-8 specific technical, geographic, and domain keywords.\n"
            "6. suggested_solution_directions: 2-4 concrete, actionable technical, engineering, research, or policy directions that universities and industry could pursue.\n"
            "7. confidence_score: A float between 0.0 and 1.0 indicating your confidence in this analysis.\n"
        )
        return prompt

    @classmethod
    def analyze_challenge_text(
        cls,
        title: str,
        description: str,
        category: Optional[str] = None,
        district: Optional[str] = None,
        people_affected: Optional[int] = None,
        client: Optional[genai.Client] = None,
    ) -> ChallengeAIAnalysisStructured:
        """Call Gemini API using google-genai SDK, parse, and strictly validate the structured output."""
        active_client = client or cls.get_client()
        prompt = cls.build_prompt(
            title=title,
            description=description,
            category=category,
            district=district,
            people_affected=people_affected,
        )

        try:
            response = active_client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ChallengeAIAnalysisStructured,
                    temperature=0.2,
                ),
            )
        except Exception as e:
            raise GeminiAPIError(f"Gemini API request failed: {str(e)}") from e

        try:
            raw_text = getattr(response, "text", None)
            if not raw_text:
                raise ValueError("Empty or null response text received from Gemini API.")
            structured_data = ChallengeAIAnalysisStructured.model_validate_json(raw_text)
            return structured_data
        except Exception as e:
            raise GeminiValidationError(
                f"Failed to parse or validate Gemini structured response: {str(e)}"
            ) from e
