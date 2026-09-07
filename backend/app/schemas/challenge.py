from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


VALID_CHALLENGE_STATUSES = {
    "submitted",
    "under_review",
    "verified",
    "assigned",
    "in_progress",
    "resolved",
    "rejected",
}


def normalize_jharkhand_state(v: Optional[str]) -> str:
    if v is None:
        return "Jharkhand"
    cleaned = v.strip()
    if cleaned.lower() != "jharkhand":
        raise ValueError("Only challenges within Jharkhand are accepted.")
    return "Jharkhand"


class ChallengeLocationResponse(BaseModel):
    id: int
    challenge_id: int
    state: str
    district: str
    block: Optional[str] = None
    panchayat: Optional[str] = None
    village: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    model_config = {"from_attributes": True}


class ChallengeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Challenge title")
    description: str = Field(..., min_length=1, description="Detailed challenge description")
    submitted_by: int = Field(..., ge=1, description="User ID of the submitter")
    category: Optional[str] = Field("General", max_length=100, description="Challenge category")
    subcategory: Optional[str] = Field(None, max_length=100, description="Optional subcategory")
    people_affected: Optional[int] = Field(None, ge=0, description="Estimated number of people affected")
    
    # Location fields
    state: str = Field("Jharkhand", description="State name (must be Jharkhand)")
    district: str = Field(..., min_length=1, max_length=100, description="District within Jharkhand")
    block: Optional[str] = Field(None, max_length=100, description="Block name")
    panchayat: Optional[str] = Field(None, max_length=100, description="Panchayat name")
    village: Optional[str] = Field(None, max_length=100, description="Village name")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="GPS Latitude")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="GPS Longitude")

    @field_validator("state", mode="before")
    @classmethod
    def validate_state(cls, v: str) -> str:
        return normalize_jharkhand_state(v)

    @field_validator("title", "description", "district")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("Field cannot be empty or whitespace only.")
        return v_clean


class ChallengeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    people_affected: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=50)
    
    # Editable location fields
    state: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, min_length=1, max_length=100)
    block: Optional[str] = Field(None, max_length=100)
    panchayat: Optional[str] = Field(None, max_length=100)
    village: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)

    @field_validator("state", mode="before")
    @classmethod
    def validate_state_update(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return normalize_jharkhand_state(v)
        return v

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip().lower()
            if cleaned not in VALID_CHALLENGE_STATUSES:
                raise ValueError(
                    f"Invalid status '{v}'. Allowed statuses: {', '.join(sorted(VALID_CHALLENGE_STATUSES))}"
                )
            return cleaned
        return v

    @field_validator("title", "description", "district", mode="before")
    @classmethod
    def strip_optional_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_clean = v.strip()
            if not v_clean:
                raise ValueError("Field cannot be empty or whitespace only.")
            return v_clean
        return v


class ChallengeResponse(BaseModel):
    id: int
    title: str
    description: str
    submitted_by: int
    status: str
    category: str
    subcategory: Optional[str] = None
    priority_score: Optional[float] = None
    people_affected: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    location: Optional[ChallengeLocationResponse] = None

    model_config = {"from_attributes": True}
