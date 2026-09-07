import math
from typing import List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.challenge import Challenge, ChallengeLocation
from app.models.user import User
from app.schemas.challenge import ChallengeCreate, ChallengeUpdate


class ChallengeService:
    @staticmethod
    def create_challenge(db: Session, challenge_in: ChallengeCreate) -> Challenge:
        # Verify submitter user exists
        user = db.query(User).filter(User.id == challenge_in.submitted_by).first()
        if not user:
            raise ValueError(f"User with ID {challenge_in.submitted_by} does not exist.")

        challenge = Challenge(
            title=challenge_in.title,
            description=challenge_in.description,
            submitted_by=challenge_in.submitted_by,
            category=challenge_in.category or "General",
            subcategory=challenge_in.subcategory,
            people_affected=challenge_in.people_affected,
            status="submitted",
        )
        db.add(challenge)
        db.flush()

        location = ChallengeLocation(
            challenge_id=challenge.id,
            state=challenge_in.state,
            district=challenge_in.district,
            block=challenge_in.block,
            panchayat=challenge_in.panchayat,
            village=challenge_in.village,
            latitude=challenge_in.latitude,
            longitude=challenge_in.longitude,
        )
        db.add(location)
        db.commit()
        db.refresh(challenge)
        return challenge

    @staticmethod
    def get_challenges(
        db: Session,
        status: Optional[str] = None,
        category: Optional[str] = None,
        district: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[Challenge], int]:
        query = db.query(Challenge).options(joinedload(Challenge.location))

        if status:
            query = query.filter(func.lower(Challenge.status) == status.strip().lower())

        if category:
            query = query.filter(func.lower(Challenge.category) == category.strip().lower())

        if district:
            query = query.join(Challenge.location).filter(
                func.lower(ChallengeLocation.district) == district.strip().lower()
            )

        total = query.distinct().count()
        offset = (page - 1) * page_size
        items = (
            query.order_by(Challenge.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return items, total

    @staticmethod
    def get_challenge_by_id(db: Session, challenge_id: int) -> Optional[Challenge]:
        return (
            db.query(Challenge)
            .options(joinedload(Challenge.location))
            .filter(Challenge.id == challenge_id)
            .first()
        )

    @staticmethod
    def update_challenge(
        db: Session, challenge_id: int, update_in: ChallengeUpdate
    ) -> Optional[Challenge]:
        challenge = ChallengeService.get_challenge_by_id(db, challenge_id)
        if not challenge:
            return None

        update_data = update_in.model_dump(exclude_unset=True)

        # Update base challenge fields
        for field in ["title", "description", "category", "subcategory", "people_affected", "status"]:
            if field in update_data:
                setattr(challenge, field, update_data[field])

        # Update location fields
        loc_fields = ["state", "district", "block", "panchayat", "village", "latitude", "longitude"]
        has_loc_update = any(f in update_data for f in loc_fields)

        if has_loc_update:
            if not challenge.location:
                challenge.location = ChallengeLocation(
                    challenge_id=challenge.id,
                    state="Jharkhand",
                    district=update_data.get("district", "Unknown"),
                )
                db.add(challenge.location)
                db.flush()

            for f in loc_fields:
                if f in update_data and update_data[f] is not None:
                    setattr(challenge.location, f, update_data[f])

        db.commit()
        db.refresh(challenge)
        return challenge
