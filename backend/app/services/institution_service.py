from typing import List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.institution import Institution, InstitutionExpertise
from app.schemas.institution import InstitutionCreate, InstitutionExpertiseCreate


class InstitutionService:
    @staticmethod
    def create_institution(db: Session, inst_in: InstitutionCreate) -> Institution:
        institution = Institution(
            name=inst_in.name,
            institution_type=inst_in.institution_type,
            district=inst_in.district,
            address=inst_in.address,
            latitude=inst_in.latitude,
            longitude=inst_in.longitude,
            website=inst_in.website,
            description=inst_in.description,
            verification_status="pending",
        )
        db.add(institution)
        db.commit()
        db.refresh(institution)
        return institution

    @staticmethod
    def get_institutions(
        db: Session,
        district: Optional[str] = None,
        institution_type: Optional[str] = None,
        verification_status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[Institution], int]:
        query = db.query(Institution)

        if district:
            query = query.filter(func.lower(Institution.district) == district.strip().lower())

        if institution_type:
            query = query.filter(
                func.lower(Institution.institution_type) == institution_type.strip().lower()
            )

        if verification_status:
            query = query.filter(
                func.lower(Institution.verification_status) == verification_status.strip().lower()
            )

        total = query.count()
        offset = (page - 1) * page_size
        items = (
            query.order_by(Institution.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return items, total

    @staticmethod
    def get_institution_by_id(db: Session, institution_id: int) -> Optional[Institution]:
        return (
            db.query(Institution)
            .options(joinedload(Institution.expertise_entries))
            .filter(Institution.id == institution_id)
            .first()
        )

    @staticmethod
    def create_institution_expertise(
        db: Session, institution_id: int, exp_in: InstitutionExpertiseCreate
    ) -> Optional[InstitutionExpertise]:
        # Check institution exists
        institution = db.query(Institution).filter(Institution.id == institution_id).first()
        if not institution:
            return None

        expertise = InstitutionExpertise(
            institution_id=institution_id,
            domain=exp_in.domain,
            subdomain=exp_in.subdomain,
            keywords=exp_in.keywords,
            expertise_level=exp_in.expertise_level,
            facilities=exp_in.facilities,
            research_areas=exp_in.research_areas,
        )
        db.add(expertise)
        db.commit()
        db.refresh(expertise)
        return expertise

    @staticmethod
    def get_institution_expertise_list(
        db: Session, institution_id: int
    ) -> Optional[List[InstitutionExpertise]]:
        institution = db.query(Institution).filter(Institution.id == institution_id).first()
        if not institution:
            return None

        return (
            db.query(InstitutionExpertise)
            .filter(InstitutionExpertise.institution_id == institution_id)
            .order_by(InstitutionExpertise.id.asc())
            .all()
        )
