from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

VALID_EXPERTISE_LEVELS = {
    "beginner",
    "intermediate",
    "advanced",
    "expert",
    "leading",
}


class InstitutionExpertiseCreate(BaseModel):
    domain: str = Field(..., min_length=1, max_length=100, description="Domain of expertise (e.g. Water Resources)")
    subdomain: Optional[str] = Field(None, max_length=100, description="Specific subdomain")
    keywords: Optional[str] = Field(None, description="Comma-separated or freeform keywords")
    expertise_level: Optional[str] = Field(
        None,
        description="Expertise level (e.g. Beginner, Intermediate, Advanced, Expert)",
    )
    facilities: Optional[str] = Field(None, description="Labs and research equipment")
    research_areas: Optional[str] = Field(None, description="Key research focus areas")

    @field_validator("domain", mode="before")
    @classmethod
    def strip_domain(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("Domain cannot be empty.")
        return v_clean

    @field_validator("expertise_level", mode="before")
    @classmethod
    def validate_expertise_level(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip().lower()
            if cleaned not in VALID_EXPERTISE_LEVELS:
                raise ValueError(
                    f"Invalid expertise_level '{v}'. Allowed levels: {', '.join(sorted(l.title() for l in VALID_EXPERTISE_LEVELS))}"
                )
            return cleaned.title()
        return v


class InstitutionExpertiseResponse(BaseModel):
    id: int
    institution_id: int
    domain: str
    subdomain: Optional[str] = None
    keywords: Optional[str] = None
    expertise_level: Optional[str] = None
    facilities: Optional[str] = None
    research_areas: Optional[str] = None

    model_config = {"from_attributes": True}


class InstitutionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Institution name")
    institution_type: str = Field(..., min_length=1, max_length=100, description="Type (e.g. Engineering, University, Research)")
    district: str = Field(..., min_length=1, max_length=100, description="District located in")
    address: Optional[str] = Field(None, description="Physical address")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="GPS Latitude")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="GPS Longitude")
    website: Optional[str] = Field(None, max_length=255, description="Official website URL")
    description: Optional[str] = Field(None, description="Description of the institution")

    @field_validator("name", "institution_type", "district", mode="before")
    @classmethod
    def strip_required_strings(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("Field cannot be empty or whitespace only.")
        return v_clean


class InstitutionResponse(BaseModel):
    id: int
    name: str
    institution_type: str
    district: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    website: Optional[str] = None
    description: Optional[str] = None
    verification_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InstitutionDetailResponse(InstitutionResponse):
    expertise_entries: List[InstitutionExpertiseResponse] = []

    model_config = {"from_attributes": True}
