from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.challenge import Challenge, ChallengeAIAnalysis
from app.schemas.ai_analysis import ChallengeAIAnalysisStructured
from app.services.gemini_service import GeminiService


class AIAnalysisService:
    @staticmethod
    def analyze_and_store_challenge(
        db: Session,
        challenge_id: int,
    ) -> ChallengeAIAnalysis:
        """Run AI analysis on a Challenge via GeminiService and persist the result."""
        challenge = (
            db.query(Challenge)
            .options(joinedload(Challenge.location))
            .filter(Challenge.id == challenge_id)
            .first()
        )

        if not challenge:
            raise ValueError(f"Challenge with ID {challenge_id} not found.")

        district = challenge.location.district if challenge.location else None

        structured_output: ChallengeAIAnalysisStructured = (
            GeminiService.analyze_challenge_text(
                title=challenge.title,
                description=challenge.description,
                category=challenge.category,
                district=district,
                people_affected=challenge.people_affected,
            )
        )

        # Convert list fields to database-friendly strings.
        keywords_str = ", ".join(structured_output.relevant_keywords)
        expertise_str = "; ".join(
            structured_output.suggested_solution_directions
        )

        # Check whether an AI analysis already exists.
        existing_analysis = (
            db.query(ChallengeAIAnalysis)
            .filter(
                ChallengeAIAnalysis.challenge_id == challenge_id
            )
            .first()
        )

        if existing_analysis:
            # Update existing analysis.
            existing_analysis.category = structured_output.detected_category
            existing_analysis.subcategory = structured_output.detected_subcategory
            existing_analysis.keywords = keywords_str
            existing_analysis.priority_score = structured_output.priority_score
            existing_analysis.required_expertise = expertise_str

            # Persist the previously missing AI fields.
            existing_analysis.problem_summary = structured_output.problem_summary
            existing_analysis.confidence_score = structured_output.confidence_score

            existing_analysis.model_version = settings.GEMINI_MODEL
            existing_analysis.created_at = datetime.now(timezone.utc)

            analysis_record = existing_analysis

        else:
            # Create a new analysis record.
            analysis_record = ChallengeAIAnalysis(
                challenge_id=challenge.id,
                category=structured_output.detected_category,
                subcategory=structured_output.detected_subcategory,
                keywords=keywords_str,
                priority_score=structured_output.priority_score,
                required_expertise=expertise_str,

                # Persist the AI-generated fields.
                problem_summary=structured_output.problem_summary,
                confidence_score=structured_output.confidence_score,

                model_version=settings.GEMINI_MODEL,
            )

            db.add(analysis_record)

        # Synchronize the challenge priority score.
        challenge.priority_score = structured_output.priority_score

        db.commit()
        db.refresh(analysis_record)

        return analysis_record

    @staticmethod
    def get_analysis_by_challenge_id(
        db: Session,
        challenge_id: int,
    ) -> Optional[ChallengeAIAnalysis]:
        """Fetch the stored AI analysis for a challenge."""
        return (
            db.query(ChallengeAIAnalysis)
            .filter(
                ChallengeAIAnalysis.challenge_id == challenge_id
            )
            .first()
        )