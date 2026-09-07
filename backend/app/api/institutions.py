import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.institution import (
    InstitutionCreate,
    InstitutionDetailResponse,
    InstitutionExpertiseCreate,
    InstitutionExpertiseResponse,
    InstitutionResponse,
)
from app.services.institution_service import InstitutionService

router = APIRouter(prefix="/api/institutions", tags=["Institutions"])


@router.post(
    "",
    response_model=InstitutionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an institution profile",
    description="Register a Higher Education Institution or Research Institute profile.",
)
def create_institution(
    payload: InstitutionCreate,
    db: Session = Depends(get_db),
):
    institution = InstitutionService.create_institution(db, payload)
    return institution


@router.get(
    "",
    response_model=PaginatedResponse[InstitutionResponse],
    status_code=status.HTTP_200_OK,
    summary="List institutions",
    description="Retrieve a paginated list of institutions with optional filters.",
)
def list_institutions(
    district: Optional[str] = Query(None, description="Filter by district"),
    institution_type: Optional[str] = Query(None, description="Filter by institution type"),
    verification_status: Optional[str] = Query(None, description="Filter by verification status"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    items, total = InstitutionService.get_institutions(
        db=db,
        district=district,
        institution_type=institution_type,
        verification_status=verification_status,
        page=page,
        page_size=page_size,
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{institution_id}",
    response_model=InstitutionDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get institution details",
    description="Retrieve institution profile along with registered expertise domains.",
)
def get_institution(
    institution_id: int,
    db: Session = Depends(get_db),
):
    institution = InstitutionService.get_institution_by_id(db, institution_id)
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institution with ID {institution_id} not found.",
        )
    return institution


@router.post(
    "/{institution_id}/expertise",
    response_model=InstitutionExpertiseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add expertise to an institution",
    description="Add a technical domain expertise entry to an institution profile.",
)
def add_institution_expertise(
    institution_id: int,
    payload: InstitutionExpertiseCreate,
    db: Session = Depends(get_db),
):
    expertise = InstitutionService.create_institution_expertise(db, institution_id, payload)
    if not expertise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institution with ID {institution_id} not found.",
        )
    return expertise


@router.get(
    "/{institution_id}/expertise",
    response_model=List[InstitutionExpertiseResponse],
    status_code=status.HTTP_200_OK,
    summary="List institution expertise domains",
    description="Retrieve all expertise entries associated with a specific institution.",
)
def get_institution_expertise(
    institution_id: int,
    db: Session = Depends(get_db),
):
    expertise_list = InstitutionService.get_institution_expertise_list(db, institution_id)
    if expertise_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institution with ID {institution_id} not found.",
        )
    return expertise_list
