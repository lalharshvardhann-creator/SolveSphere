import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.challenge import ChallengeCreate, ChallengeResponse, ChallengeUpdate
from app.schemas.common import PaginatedResponse
from app.services.challenge_service import ChallengeService

router = APIRouter(prefix="/api/challenges", tags=["Challenges"])


@router.post(
    "",
    response_model=ChallengeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new societal challenge",
    description="Submit a new societal challenge situated within Jharkhand.",
)
def create_challenge(
    payload: ChallengeCreate,
    db: Session = Depends(get_db),
):
    try:
        challenge = ChallengeService.create_challenge(db, payload)
        return challenge
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=PaginatedResponse[ChallengeResponse],
    status_code=status.HTTP_200_OK,
    summary="List societal challenges",
    description="Retrieve a paginated list of challenges with optional filters for status, category, and district.",
)
def list_challenges(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by challenge status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    district: Optional[str] = Query(None, description="Filter by district"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    items, total = ChallengeService.get_challenges(
        db=db,
        status=status_filter,
        category=category,
        district=district,
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
    "/{challenge_id}",
    response_model=ChallengeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get challenge details",
    description="Retrieve full details and location information for a specific challenge.",
)
def get_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
):
    challenge = ChallengeService.get_challenge_by_id(db, challenge_id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge with ID {challenge_id} not found.",
        )
    return challenge


@router.patch(
    "/{challenge_id}",
    response_model=ChallengeResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a challenge",
    description="Safely update editable fields of a challenge and its location.",
)
def update_challenge(
    challenge_id: int,
    payload: ChallengeUpdate,
    db: Session = Depends(get_db),
):
    challenge = ChallengeService.update_challenge(db, challenge_id, payload)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge with ID {challenge_id} not found.",
        )
    return challenge
