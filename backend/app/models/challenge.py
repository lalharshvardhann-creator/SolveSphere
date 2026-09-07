from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.institution import Institution
    from app.models.project import Project
    from app.models.user import User


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), default="submitted", nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    priority_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    people_affected: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
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

    submitter: Mapped["User"] = relationship("User", back_populates="challenges")
    location: Mapped[Optional["ChallengeLocation"]] = relationship(
        "ChallengeLocation",
        back_populates="challenge",
        uselist=False,
        cascade="all, delete-orphan",
    )
    evidence_items: Mapped[List["ChallengeEvidence"]] = relationship(
        "ChallengeEvidence",
        back_populates="challenge",
        cascade="all, delete-orphan",
    )
    ai_analysis: Mapped[Optional["ChallengeAIAnalysis"]] = relationship(
        "ChallengeAIAnalysis",
        back_populates="challenge",
        uselist=False,
        cascade="all, delete-orphan",
    )
    assignments: Mapped[List["ChallengeAssignment"]] = relationship(
        "ChallengeAssignment",
        back_populates="challenge",
        cascade="all, delete-orphan",
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="challenge",
    )


class ChallengeLocation(Base):
    __tablename__ = "challenge_locations"
    __table_args__ = (
        CheckConstraint("state = 'Jharkhand'", name="ck_challenge_location_jharkhand_only"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    challenge_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    state: Mapped[str] = mapped_column(String(100), default="Jharkhand", nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    block: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    panchayat: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    village: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="location")


class ChallengeEvidence(Base):
    __tablename__ = "challenge_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    challenge_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="evidence_items")
    uploader: Mapped[Optional["User"]] = relationship("User")


class ChallengeAIAnalysis(Base):
    __tablename__ = "challenge_ai_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    challenge_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    duplicate_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    required_expertise: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="ai_analysis")


class ChallengeAssignment(Base):
    __tablename__ = "challenge_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    challenge_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    institution_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    match_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="proposed", nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="assignments")
    institution: Mapped["Institution"] = relationship("Institution", back_populates="assignments")
