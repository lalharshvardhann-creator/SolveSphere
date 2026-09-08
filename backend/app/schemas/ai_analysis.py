from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ChallengeAIAnalysisStructured(BaseModel):
    """Structured response model generated and strictly validated from Gemini AI analysis."""
    problem_summary: str = Field(
        ...,
        min_length=5,
        description="Concise summary of the societal challenge and key issues identified",
    )
    detected_category: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Assessed domain category (e.g., Water Supply, Healthcare, Agriculture, Infrastructure, Education, Sanitation)",
    )
    detected_subcategory: Optional[str] = Field(
        None,
        max_length=100,
        description="Specific subcategory or sub-domain classification",
    )
    priority_score: float = Field(
        ...,
        ge=1.0,
        le=10.0,
        description="Assessed urgency and severity score from 1.0 (lowest) to 10.0 (critical)",
    )
    relevant_keywords: List[str] = Field(
        default_factory=list,
        description="Key domain terms, technologies, and geographic/topical keywords",
    )
    suggested_solution_directions: List[str] = Field(
        default_factory=list,
        description="Actionable technical, engineering, research, or policy solution directions",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="AI confidence score between 0.0 and 1.0",
    )


class ChallengeAIAnalysisResponse(BaseModel):
    """API response model representing stored AI analysis for a challenge."""
    id: int
    challenge_id: int
    category: Optional[str] = None
    subcategory: Optional[str] = None
    keywords: Optional[str] = None
    priority_score: Optional[float] = None
    duplicate_score: Optional[float] = None
    required_expertise: Optional[str] = None
    model_version: Optional[str] = None
    created_at: datetime
    problem_summary: Optional[str] = None
    confidence_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
