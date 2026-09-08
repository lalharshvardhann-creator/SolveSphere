import json
from unittest.mock import MagicMock, patch
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.models.challenge import Challenge, ChallengeAIAnalysis, ChallengeLocation
from app.models.user import User


@pytest.fixture
def sample_challenge(db_session: Session, test_user: User) -> Challenge:
    """Fixture to create a sample challenge situated in Jharkhand."""
    challenge = Challenge(
        title="Severe groundwater arsenic contamination in rural Ranchi",
        description="High levels of arsenic detected in village handpumps exceeding WHO limits, causing chronic skin conditions.",
        submitted_by=test_user.id,
        category="Water Supply",
        subcategory="Groundwater Quality",
        people_affected=3500,
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
    db_session.commit()
    db_session.refresh(challenge)
    return challenge


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Fixture providing valid Authorization header with Bearer JWT."""
    token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email, "role": test_user.role})
    return {"Authorization": f"Bearer {token}"}


class MockGeminiResponse:
    def __init__(self, text: str):
        self.text = text


VALID_GEMINI_OUTPUT = json.dumps({
    "problem_summary": "Arsenic contamination in drinking groundwater exceeding safety levels in rural Ranchi.",
    "detected_category": "Water Supply",
    "detected_subcategory": "Groundwater Contamination",
    "priority_score": 8.5,
    "relevant_keywords": ["arsenic", "groundwater", "filtration", "ranchi", "water safety"],
    "suggested_solution_directions": [
        "Deploy modular adsorption filtration units",
        "Implement community IoT water quality sensing",
    ],
    "confidence_score": 0.94,
})


def test_analyze_challenge_success_mocked(
    client: TestClient,
    db_session: Session,
    sample_challenge: Challenge,
    auth_headers: dict,
):
    """Test successful AI analysis triggers Gemini, validates output, and stores to database."""
    with patch.object(settings, "GEMINI_API_KEY", "test-valid-api-key"):
        with patch("google.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            mock_client.models.generate_content.return_value = MockGeminiResponse(VALID_GEMINI_OUTPUT)

            response = client.post(
                f"/api/challenges/{sample_challenge.id}/analyze",
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["challenge_id"] == sample_challenge.id
            assert data["category"] == "Water Supply"
            assert data["subcategory"] == "Groundwater Contamination"
            assert "arsenic" in data["keywords"]
            assert data["priority_score"] == 8.5
            assert "Deploy modular adsorption" in data["required_expertise"]
            assert data["model_version"] == settings.GEMINI_MODEL
            assert data["problem_summary"] == "Arsenic contamination in drinking groundwater exceeding safety levels in rural Ranchi."
            assert data["confidence_score"] == 0.94

            # Verify persistence in database
            stored = (
                db_session.query(ChallengeAIAnalysis)
                .filter(ChallengeAIAnalysis.challenge_id == sample_challenge.id)
                .first()
            )
            assert stored is not None
            assert stored.category == "Water Supply"
            assert stored.priority_score == 8.5

            # Verify challenge priority_score updated
            db_session.refresh(sample_challenge)
            assert sample_challenge.priority_score == 8.5


def test_analyze_challenge_reanalysis_upsert(
    client: TestClient,
    db_session: Session,
    sample_challenge: Challenge,
    auth_headers: dict,
):
    """Test triggering analysis twice on the same challenge updates the existing record without violation."""
    with patch.object(settings, "GEMINI_API_KEY", "test-valid-api-key"):
        with patch("google.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client

            # First run
            mock_client.models.generate_content.return_value = MockGeminiResponse(VALID_GEMINI_OUTPUT)
            resp1 = client.post(f"/api/challenges/{sample_challenge.id}/analyze", headers=auth_headers)
            assert resp1.status_code == status.HTTP_200_OK

            # Second run with updated priority score
            updated_output = json.dumps({
                "problem_summary": "Updated summary of water issue.",
                "detected_category": "Environmental Health",
                "detected_subcategory": "Heavy Metal Poisoning",
                "priority_score": 9.2,
                "relevant_keywords": ["arsenic", "toxicology"],
                "suggested_solution_directions": ["Deep aquifer exploration"],
                "confidence_score": 0.98,
            })
            mock_client.models.generate_content.return_value = MockGeminiResponse(updated_output)
            resp2 = client.post(f"/api/challenges/{sample_challenge.id}/analyze", headers=auth_headers)
            assert resp2.status_code == status.HTTP_200_OK
            data2 = resp2.json()
            assert data2["category"] == "Environmental Health"
            assert data2["priority_score"] == 9.2

            # Ensure only 1 record exists in DB for this challenge
            count = (
                db_session.query(ChallengeAIAnalysis)
                .filter(ChallengeAIAnalysis.challenge_id == sample_challenge.id)
                .count()
            )
            assert count == 1


def test_analyze_challenge_malformed_response(
    client: TestClient,
    sample_challenge: Challenge,
    auth_headers: dict,
):
    """Test handling of malformed or schema-invalid JSON from Gemini."""
    with patch.object(settings, "GEMINI_API_KEY", "test-valid-api-key"):
        with patch("google.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            # Missing required fields like priority_score and confidence_score
            mock_client.models.generate_content.return_value = MockGeminiResponse(
                '{"invalid_field": "some bad data"}'
            )

            response = client.post(
                f"/api/challenges/{sample_challenge.id}/analyze",
                headers=auth_headers,
            )
            assert response.status_code == status.HTTP_502_BAD_GATEWAY
            assert "validation error" in response.json()["detail"].lower()


def test_analyze_challenge_gemini_api_exception(
    client: TestClient,
    sample_challenge: Challenge,
    auth_headers: dict,
):
    """Test handling of network/API errors when communicating with Gemini."""
    with patch.object(settings, "GEMINI_API_KEY", "test-valid-api-key"):
        with patch("google.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            mock_client.models.generate_content.side_effect = RuntimeError("Quota exceeded or connection error")

            response = client.post(
                f"/api/challenges/{sample_challenge.id}/analyze",
                headers=auth_headers,
            )
            assert response.status_code == status.HTTP_502_BAD_GATEWAY
            assert "AI service error" in response.json()["detail"]


def test_analyze_challenge_missing_api_key(
    client: TestClient,
    sample_challenge: Challenge,
    auth_headers: dict,
):
    """Test 503 Service Unavailable is returned when GEMINI_API_KEY is not configured."""
    with patch.object(settings, "GEMINI_API_KEY", None):
        response = client.post(
            f"/api/challenges/{sample_challenge.id}/analyze",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "not configured" in response.json()["detail"].lower()


def test_analyze_challenge_not_found(
    client: TestClient,
    auth_headers: dict,
):
    """Test 404 is returned when analyzing a nonexistent challenge."""
    with patch.object(settings, "GEMINI_API_KEY", "test-api-key"):
        response = client.post(
            "/api/challenges/99999/analyze",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


def test_analyze_challenge_unauthenticated(
    client: TestClient,
    sample_challenge: Challenge,
):
    """Test 401 is returned when analyzing without authentication token."""
    response = client.post(f"/api/challenges/{sample_challenge.id}/analyze")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_ai_analysis_endpoint(
    client: TestClient,
    db_session: Session,
    sample_challenge: Challenge,
    auth_headers: dict,
):
    """Test GET /api/challenges/{id}/ai-analysis returns stored analysis."""
    # Initially 404
    resp_before = client.get(f"/api/challenges/{sample_challenge.id}/ai-analysis")
    assert resp_before.status_code == status.HTTP_404_NOT_FOUND

    # Manually add analysis record
    analysis = ChallengeAIAnalysis(
        challenge_id=sample_challenge.id,
        category="Sanitation",
        subcategory="Waste Management",
        keywords="solid waste, composting",
        priority_score=7.0,
        required_expertise="Environmental Engineering",
        model_version="gemini-2.5-flash",
    )
    db_session.add(analysis)
    db_session.commit()

    # Now GET returns 200 OK
    resp_after = client.get(f"/api/challenges/{sample_challenge.id}/ai-analysis")
    assert resp_after.status_code == status.HTTP_200_OK
    data = resp_after.json()
    assert data["challenge_id"] == sample_challenge.id
    assert data["category"] == "Sanitation"
    assert data["priority_score"] == 7.0
