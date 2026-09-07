from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.challenge import ChallengeAssignment
    from app.models.project import Project


class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    institution_type: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    expertise_entries: Mapped[List["InstitutionExpertise"]] = relationship(
        "InstitutionExpertise",
        back_populates="institution",
        cascade="all, delete-orphan",
    )
    assignments: Mapped[List["ChallengeAssignment"]] = relationship(
        "ChallengeAssignment",
        back_populates="institution",
        cascade="all, delete-orphan",
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="institution",
    )


class InstitutionExpertise(Base):
    __tablename__ = "institution_expertise"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    institution_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    domain: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subdomain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expertise_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    facilities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    research_areas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    institution: Mapped["Institution"] = relationship(
        "Institution",
        back_populates="expertise_entries",
    )
