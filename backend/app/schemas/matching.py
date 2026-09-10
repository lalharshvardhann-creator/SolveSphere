from typing import List
from pydantic import BaseModel, ConfigDict, Field


class InstitutionMatchItem(BaseModel):
    institution_id: int = Field(..., description="Unique ID of the matched institution")
    institution_name: str = Field(..., description="Name of the institution")
    institution_type: str = Field(..., description="Type of the institution (e.g. Research, University)")
    district: str = Field(..., description="District where the institution is located")
    match_score: float = Field(..., ge=0.0, le=100.0, description="Deterministic match score between 0.0 and 100.0")
    match_reason: str = Field(..., description="Human-readable explanation of why the institution matched")

    model_config = ConfigDict(from_attributes=True)


class ChallengeMatchResponse(BaseModel):
    challenge_id: int = Field(..., description="ID of the challenge matched against")
    matches: List[InstitutionMatchItem] = Field(
        default_factory=list,
        description="Ranked list of matching institutions",
    )

    model_config = ConfigDict(from_attributes=True)
