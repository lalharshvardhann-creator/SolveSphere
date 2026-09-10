import os
from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.main import app
from app.models import (
    Challenge,
    ChallengeAIAnalysis,
    ChallengeAssignment,
    ChallengeEvidence,
    ChallengeLocation,
    ImpactMetric,
    IndustryPartner,
    Institution,
    InstitutionExpertise,
    Milestone,
    Notification,
    Project,
    ProjectCollaboration,
    ProjectMember,
    User,
)


def test_models_import_and_metadata_registered():
    """Verify all 15 models are properly mapped and registered in metadata."""
    expected_tables = {
        "users",
        "institutions",
        "institution_expertise",
        "challenges",
        "challenge_locations",
        "challenge_evidence",
        "challenge_ai_analysis",
        "challenge_assignments",
        "projects",
        "project_members",
        "industry_partners",
        "project_collaborations",
        "milestones",
        "impact_metrics",
        "notifications",
    }
    registered_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(registered_tables)


def test_sqlite_schema_creation_and_fk_mappings():
    """Verify SQLite can build all tables and foreign key relationships without mapper errors."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(test_engine)

    TestSession = sessionmaker(bind=test_engine)
    session: Session = TestSession()

    # Create User
    user = User(
        name="Ramesh Soren",
        email="ramesh@example.com",
        password_hash="hashed_pw_placeholder",
        role="citizen",
        phone="9876543210",
        preferred_language="hi",
    )
    session.add(user)
    session.commit()

    # Create Institution & Expertise
    inst = Institution(
        name="BIT Mesra",
        institution_type="Engineering",
        district="Ranchi",
        address="Mesra, Ranchi",
        website="https://www.bitmesra.ac.in",
    )
    session.add(inst)
    session.commit()

    expertise = InstitutionExpertise(
        institution_id=inst.id,
        domain="Water Resources",
        subdomain="Groundwater Management",
        keywords="groundwater, hydrology, tribal water security",
    )
    session.add(expertise)
    session.commit()

    # Create Challenge & Location
    challenge = Challenge(
        title="Water Scarcity in Khunti",
        description="Severe water scarcity during dry seasons in tribal blocks.",
        submitted_by=user.id,
        category="Water & Sanitation",
        subcategory="Groundwater Depletion",
    )
    session.add(challenge)
    session.commit()

    location = ChallengeLocation(
        challenge_id=challenge.id,
        state="Jharkhand",
        district="Khunti",
        block="Murhu",
        panchayat="Torpa Road",
        village="Banda",
    )
    session.add(location)

    # Challenge Evidence & AI Analysis
    evidence = ChallengeEvidence(
        challenge_id=challenge.id,
        file_type="image/jpeg",
        file_url="https://storage.solvesphere.jh/ev/dry_well.jpg",
        description="Dry community well in May",
        uploaded_by=user.id,
    )
    ai_analysis = ChallengeAIAnalysis(
        challenge_id=challenge.id,
        category="Water Resources",
        subcategory="Groundwater",
        keywords="water, drought, community wells",
        priority_score=0.85,
        required_expertise="Hydrology, Civil Engineering",
        model_version="v1.0",
    )
    session.add_all([evidence, ai_analysis])
    session.commit()

    # Challenge Assignment
    assignment = ChallengeAssignment(
        challenge_id=challenge.id,
        institution_id=inst.id,
        match_score=0.92,
        match_reason="Strong faculty expertise in groundwater hydrology.",
        status="proposed",
    )
    session.add(assignment)
    session.commit()

    # Project & Project Member
    project = Project(
        challenge_id=challenge.id,
        institution_id=inst.id,
        title="Murhu Aquifer Recharge Pilot",
        description="Community recharge wells for year-round drinking water.",
        status="planning",
    )
    session.add(project)
    session.commit()

    member = ProjectMember(
        project_id=project.id,
        user_id=user.id,
        role="Community Lead",
    )
    session.add(member)

    # Industry Partner & Collaboration
    partner = IndustryPartner(
        name="Tata Steel Foundation",
        partner_type="CSR",
        district="East Singhbhum",
        website="https://tatasteelfoundation.org",
        expertise="Rural livelihoods and community water infrastructure",
    )
    session.add(partner)
    session.commit()

    collab = ProjectCollaboration(
        project_id=project.id,
        partner_id=partner.id,
        collaboration_type="Funding & CSR Support",
        description="Co-financing borehole surveys and community mobilization.",
    )
    session.add(collab)

    # Milestone & Impact Metric
    milestone = Milestone(
        project_id=project.id,
        title="Geological Survey Completed",
        status="pending",
    )
    metric = ImpactMetric(
        project_id=project.id,
        metric_name="Households Benefitted",
        metric_value=450.0,
        unit="Households",
        description="Tribal families with sustainable water access",
    )
    session.add_all([milestone, metric])

    # Notification
    notification = Notification(
        user_id=user.id,
        title="Challenge Update",
        message="Your challenge has been assigned to BIT Mesra.",
        notification_type="status_update",
    )
    session.add(notification)
    session.commit()

    # Assert relations
    assert len(user.challenges) == 1
    assert user.challenges[0].title == "Water Scarcity in Khunti"
    assert challenge.location.district == "Khunti"
    assert len(inst.expertise_entries) == 1
    assert project.institution.name == "BIT Mesra"
    assert len(project.members) == 1
    assert len(project.collaborations) == 1
    assert len(project.milestones) == 1
    assert len(project.impact_metrics) == 1
    assert len(user.notifications) == 1

    session.close()


def test_alembic_configuration():
    """Verify Alembic configuration and revision script directory."""
    alembic_ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
    assert os.path.exists(alembic_ini_path)

    config = Config(alembic_ini_path)
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    assert len(heads) == 1
    assert heads[0] == "d60d18122ebc"



def test_fastapi_app_and_health_endpoint():
    """Verify FastAPI application starts and GET /health returns expected response."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "SolveSphere API",
    }
