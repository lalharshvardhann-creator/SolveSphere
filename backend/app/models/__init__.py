"""SQLAlchemy models package for SolveSphere."""
from app.models.challenge import (
    Challenge,
    ChallengeAIAnalysis,
    ChallengeAssignment,
    ChallengeEvidence,
    ChallengeLocation,
)
from app.models.institution import Institution, InstitutionExpertise
from app.models.notification import Notification
from app.models.partner import IndustryPartner, ProjectCollaboration
from app.models.project import ImpactMetric, Milestone, Project, ProjectMember
from app.models.user import User

__all__ = [
    "User",
    "Institution",
    "InstitutionExpertise",
    "Challenge",
    "ChallengeLocation",
    "ChallengeEvidence",
    "ChallengeAIAnalysis",
    "ChallengeAssignment",
    "Project",
    "ProjectMember",
    "IndustryPartner",
    "ProjectCollaboration",
    "Milestone",
    "ImpactMetric",
    "Notification",
]
