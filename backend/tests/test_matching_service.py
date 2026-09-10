import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.challenge import (
    Challenge,
    ChallengeAIAnalysis,
    ChallengeAssignment,
    ChallengeLocation,
)
from app.models.institution import Institution, InstitutionExpertise
from app.models.user import User
from app.services.matching_service import MatchingService


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Fixture providing valid Authorization header with Bearer JWT."""
    token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email, "role": test_user.role}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def clean_water_challenge(db_session: Session, test_user: User) -> Challenge:
    """Fixture creating Challenge #3: Clean Drinking Water with AI Analysis."""
    challenge = Challenge(
        title="Clean Drinking Water",
        description="Severe groundwater arsenic contamination and lack of clean drinking water in rural Ranchi villages.",
        submitted_by=test_user.id,
        category="Water Supply",
        subcategory="Rural Water Purification and Distribution",
        priority_score=8.5,
        people_affected=5000,
        status="submitted",
    )
    db_session.add(challenge)
    db_session.flush()

    location = ChallengeLocation(
        challenge_id=challenge.id,
        state="Jharkhand",
        district="Ranchi",
        block="Kanke",
        village="Pithoria",
        latitude=23.456,
        longitude=85.312,
    )
    db_session.add(location)

    ai_analysis = ChallengeAIAnalysis(
        challenge_id=challenge.id,
        category="Water Supply",
        subcategory="Rural Water Purification and Distribution",
        keywords="water filtration, groundwater quality, drinking water, IoT water monitoring, rainwater harvesting, arsenic",
        priority_score=8.5,
        required_expertise="water filtration; groundwater quality; IoT water monitoring; rainwater harvesting; rural water purification",
        problem_summary="Arsenic contamination in drinking water sources across rural Ranchi requiring modular filtration and water quality monitoring.",
        confidence_score=0.95,
        model_version="gemini-2.5-flash",
    )
    db_session.add(ai_analysis)
    db_session.commit()
    db_session.refresh(challenge)
    return challenge


@pytest.fixture
def setup_test_institutions(db_session: Session) -> tuple[Institution, Institution]:
    """
    Fixture creating:
    - Institution 1: Jharkhand Water Research Institute (Water Supply / Rural Water Purification)
    - Institution 2: Jharkhand Agriculture Innovation Center (Agriculture / Smart Irrigation)
    """
    # Institution 1: Water
    water_inst = Institution(
        name="Jharkhand Water Research Institute",
        institution_type="Research",
        district="Ranchi",
        address="Kanke Road, Ranchi",
        website="https://jwri.res.in",
        description="Premier research institute specializing in water resource management, rural purification systems, and hydrological survey.",
        verification_status="verified",
    )
    db_session.add(water_inst)
    db_session.flush()

    water_exp = InstitutionExpertise(
        institution_id=water_inst.id,
        domain="Water Supply",
        subdomain="Rural Water Purification",
        keywords="water filtration, groundwater quality, drinking water, IoT water monitoring, rainwater harvesting",
        expertise_level="Expert",
        facilities="Water Testing Lab, Spectrometer, Filtration Testbed",
        research_areas="rural water purification, groundwater contamination, community water systems, sustainable water management",
    )
    db_session.add(water_exp)

    # Institution 2: Agriculture
    agri_inst = Institution(
        name="Jharkhand Agriculture Innovation Center",
        institution_type="Research",
        district="Ranchi",
        address="Ring Road, Ranchi",
        website="https://jaic.res.in",
        description="State center for crop technology, soil health, and precision agricultural innovations.",
        verification_status="verified",
    )
    db_session.add(agri_inst)
    db_session.flush()

    agri_exp = InstitutionExpertise(
        institution_id=agri_inst.id,
        domain="Agriculture",
        subdomain="Smart Irrigation",
        keywords="soil health, crop technology, irrigation, precision agriculture, farm sensors",
        expertise_level="Expert",
        facilities="Soil Testing Lab, Drone Facility",
        research_areas="smart irrigation, soil health, precision agriculture, rural livelihoods",
    )
    db_session.add(agri_exp)

    db_session.commit()
    db_session.refresh(water_inst)
    db_session.refresh(agri_inst)
    return water_inst, agri_inst


def test_water_ranks_higher_than_agriculture(
    db_session: Session,
    clean_water_challenge: Challenge,
    setup_test_institutions: tuple[Institution, Institution],
):
    """Verify that the Water Research Institute ranks significantly higher than Agriculture Center for Water challenge."""
    water_inst, agri_inst = setup_test_institutions

    matches = MatchingService.match_challenge(db_session, clean_water_challenge.id)

    assert len(matches) == 2
    # First match should be the water institute
    assert matches[0]["institution_id"] == water_inst.id
    assert matches[0]["institution_name"] == "Jharkhand Water Research Institute"
    assert matches[0]["match_score"] >= 80.0
    assert "Water Supply" in matches[0]["match_reason"]
    assert "water filtration" in matches[0]["match_reason"] or "groundwater quality" in matches[0]["match_reason"]

    # Second match should be the agriculture institute
    assert matches[1]["institution_id"] == agri_inst.id
    assert matches[1]["institution_name"] == "Jharkhand Agriculture Innovation Center"
    assert matches[1]["match_score"] < 40.0

    # Ensure water institution scored significantly higher
    assert matches[0]["match_score"] > matches[1]["match_score"] + 40.0


def test_match_score_bounds_and_determinism(
    db_session: Session,
    clean_water_challenge: Challenge,
    setup_test_institutions: tuple[Institution, Institution],
):
    """Verify match scores remain strictly between 0.0 and 100.0 and are deterministic across repeated runs."""
    matches_run1 = MatchingService.match_challenge(db_session, clean_water_challenge.id)
    matches_run2 = MatchingService.match_challenge(db_session, clean_water_challenge.id)

    for m in matches_run1:
        assert 0.0 <= m["match_score"] <= 100.0

    assert len(matches_run1) == len(matches_run2)
    for m1, m2 in zip(matches_run1, matches_run2):
        assert m1["institution_id"] == m2["institution_id"]
        assert m1["match_score"] == m2["match_score"]
        assert m1["match_reason"] == m2["match_reason"]


def test_no_ai_analysis_produces_clear_error(
    db_session: Session,
    test_user: User,
    setup_test_institutions: tuple[Institution, Institution],
):
    """Verify matching fails with explicit message if AI analysis has not been executed yet."""
    challenge = Challenge(
        title="Unanalyzed Road Repair Challenge",
        description="Potholes and broken bridge in Dhanbad.",
        submitted_by=test_user.id,
        category="Infrastructure",
        status="submitted",
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)

    with pytest.raises(ValueError) as exc_info:
        MatchingService.match_challenge(db_session, challenge.id)

    assert "Challenge must be analyzed by Gemini before institution matching." in str(exc_info.value)


def test_no_institutions_returns_empty_result(
    db_session: Session,
    clean_water_challenge: Challenge,
):
    """Verify that when no institutions are registered in the DB, an empty list is returned safely."""
    matches = MatchingService.match_challenge(db_session, clean_water_challenge.id)
    assert matches == []


def test_repeated_matching_does_not_create_duplicate_assignments(
    db_session: Session,
    clean_water_challenge: Challenge,
    setup_test_institutions: tuple[Institution, Institution],
):
    """Verify repeated matching cleans previous 'proposed' assignments and prevents duplication."""
    water_inst, agri_inst = setup_test_institutions

    # First match
    MatchingService.match_challenge(db_session, clean_water_challenge.id)
    assignments_count_1 = (
        db_session.query(ChallengeAssignment)
        .filter(ChallengeAssignment.challenge_id == clean_water_challenge.id)
        .count()
    )
    assert assignments_count_1 == 2

    # Second match
    MatchingService.match_challenge(db_session, clean_water_challenge.id)
    assignments_count_2 = (
        db_session.query(ChallengeAssignment)
        .filter(ChallengeAssignment.challenge_id == clean_water_challenge.id)
        .count()
    )
    assert assignments_count_2 == 2


def test_preserve_non_proposed_assignments(
    db_session: Session,
    clean_water_challenge: Challenge,
    setup_test_institutions: tuple[Institution, Institution],
):
    """Verify existing non-proposed assignments (e.g. status='assigned') are preserved across matching runs."""
    water_inst, agri_inst = setup_test_institutions

    # Manually create a confirmed assignment
    confirmed_assignment = ChallengeAssignment(
        challenge_id=clean_water_challenge.id,
        institution_id=water_inst.id,
        match_score=95.0,
        match_reason="Previously assigned manually by admin",
        status="assigned",
    )
    db_session.add(confirmed_assignment)
    db_session.commit()

    # Run matching
    matches = MatchingService.match_challenge(db_session, clean_water_challenge.id)

    all_assignments = (
        db_session.query(ChallengeAssignment)
        .filter(ChallengeAssignment.challenge_id == clean_water_challenge.id)
        .all()
    )

    # One is assigned (water), one is proposed (agri)
    statuses = {a.institution_id: a.status for a in all_assignments}
    assert statuses[water_inst.id] == "assigned"
    assert statuses[agri_inst.id] == "proposed"


def test_api_match_endpoint_success(
    client: TestClient,
    clean_water_challenge: Challenge,
    setup_test_institutions: tuple[Institution, Institution],
    auth_headers: dict,
):
    """Test POST /api/challenges/{id}/match successfully returns ranked response."""
    water_inst, agri_inst = setup_test_institutions

    response = client.post(
        f"/api/challenges/{clean_water_challenge.id}/match",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["challenge_id"] == clean_water_challenge.id
    assert len(data["matches"]) == 2
    assert data["matches"][0]["institution_id"] == water_inst.id
    assert data["matches"][0]["institution_name"] == "Jharkhand Water Research Institute"
    assert data["matches"][0]["district"] == "Ranchi"
    assert data["matches"][0]["match_score"] >= 80.0
    assert data["matches"][1]["institution_id"] == agri_inst.id


def test_api_match_endpoint_requires_auth(
    client: TestClient,
    clean_water_challenge: Challenge,
):
    """Test POST /api/challenges/{id}/match returns 401 Unauthorized without JWT."""
    response = client.post(f"/api/challenges/{clean_water_challenge.id}/match")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_match_endpoint_no_ai_analysis_error(
    client: TestClient,
    test_user: User,
    auth_headers: dict,
    setup_test_institutions: tuple[Institution, Institution],
    db_session: Session,
):
    """Test POST /api/challenges/{id}/match returns 400 when AI analysis is absent."""
    challenge = Challenge(
        title="No Analysis Challenge",
        description="Just created challenge without AI analysis.",
        submitted_by=test_user.id,
        category="Sanitation",
        status="submitted",
    )
    db_session.add(challenge)
    db_session.commit()

    response = client.post(
        f"/api/challenges/{challenge.id}/match",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Challenge must be analyzed by Gemini before institution matching." in response.json()["detail"]


def test_api_match_endpoint_not_found(
    client: TestClient,
    auth_headers: dict,
):
    """Test POST /api/challenges/{id}/match returns 404 for non-existent challenge ID."""
    response = client.post(
        "/api/challenges/99999/match",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_api_get_matches_endpoint(
    client: TestClient,
    clean_water_challenge: Challenge,
    setup_test_institutions: tuple[Institution, Institution],
    auth_headers: dict,
):
    """Test GET /api/challenges/{id}/matches retrieves previously persisted proposed matches."""
    # First trigger matching
    client.post(
        f"/api/challenges/{clean_water_challenge.id}/match",
        headers=auth_headers,
    )

    # Then retrieve stored matches
    response = client.get(f"/api/challenges/{clean_water_challenge.id}/matches")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["challenge_id"] == clean_water_challenge.id
    assert len(data["matches"]) == 2
    assert data["matches"][0]["institution_name"] == "Jharkhand Water Research Institute"
