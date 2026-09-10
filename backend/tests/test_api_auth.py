from datetime import timedelta
import pytest
from fastapi import APIRouter, Depends, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_current_user, require_role
from app.core.security import create_access_token, get_password_hash, verify_password
from app.main import app
from app.models.user import User


# Setup a dedicated test router to verify require_role in actual HTTP requests
role_test_router = APIRouter(prefix="/api/test-roles", tags=["Role Tests"])


@role_test_router.get("/admin-only")
def admin_only_route(current_user: User = Depends(require_role("government_admin"))):
    return {"message": "Welcome Admin", "user": current_user.name, "role": current_user.role}


@role_test_router.get("/university-only")
def university_only_route(current_user: User = Depends(require_role("university"))):
    return {"message": "Welcome University", "user": current_user.name, "role": current_user.role}


@role_test_router.get("/faculty-or-university")
def faculty_or_university_route(
    current_user: User = Depends(require_role("faculty", "university")),
):
    return {"message": "Welcome Scholar", "user": current_user.name, "role": current_user.role}


# Include role_test_router in app for the tests
app.include_router(role_test_router)


def test_register_user_success(client: TestClient, db_session: Session):
    """Test successful user registration with valid data."""
    payload = {
        "name": "Ramesh Oraon",
        "email": "ramesh.oraon@example.com",
        "password": "SecurePassword123!",
        "role": "student",
        "phone": "9876543210",
        "preferred_language": "hi",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Ramesh Oraon"
    assert data["email"] == "ramesh.oraon@example.com"
    assert data["role"] == "student"
    assert data["phone"] == "9876543210"
    assert data["preferred_language"] == "hi"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Verify no password or hash is returned
    assert "password" not in data
    assert "password_hash" not in data

    # Verify database state
    user_in_db = db_session.query(User).filter(User.email == "ramesh.oraon@example.com").first()
    assert user_in_db is not None
    assert user_in_db.name == "Ramesh Oraon"
    assert user_in_db.password_hash != "SecurePassword123!"
    assert verify_password("SecurePassword123!", user_in_db.password_hash) is True


def test_register_duplicate_email(client: TestClient):
    """Test that registering with an already existing email returns an error."""
    payload = {
        "name": "User One",
        "email": "duplicate@solvesphere.jh",
        "password": "Password123!",
        "role": "citizen",
    }
    resp1 = client.post("/api/auth/register", json=payload)
    assert resp1.status_code == status.HTTP_201_CREATED

    # Attempt registration with duplicate email (different casing)
    duplicate_payload = {
        "name": "User Two",
        "email": "DUPLICATE@solvesphere.jh",
        "password": "AnotherPassword456!",
        "role": "industry",
    }
    resp2 = client.post("/api/auth/register", json=duplicate_payload)
    assert resp2.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in resp2.json()["detail"].lower()


def test_register_invalid_role(client: TestClient):
    """Test that registering with an invalid role returns validation error."""
    payload = {
        "name": "Hacker",
        "email": "hacker@solvesphere.jh",
        "password": "Password123!",
        "role": "super_admin_fake",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json().get("detail", [])
    assert any("Invalid role" in str(err) for err in errors)


def test_password_hash_security(client: TestClient, db_session: Session):
    """Test password is never stored as plaintext in DB and hashes are different across users with same password."""
    p1 = {
        "name": "User A",
        "email": "usera@solvesphere.jh",
        "password": "IdenticalPassword123!",
        "role": "citizen",
    }
    p2 = {
        "name": "User B",
        "email": "userb@solvesphere.jh",
        "password": "IdenticalPassword123!",
        "role": "faculty",
    }
    resp1 = client.post("/api/auth/register", json=p1)
    resp2 = client.post("/api/auth/register", json=p2)
    assert resp1.status_code == status.HTTP_201_CREATED
    assert resp2.status_code == status.HTTP_201_CREATED

    u1 = db_session.query(User).filter(User.email == "usera@solvesphere.jh").first()
    u2 = db_session.query(User).filter(User.email == "userb@solvesphere.jh").first()

    assert u1.password_hash != "IdenticalPassword123!"
    assert u2.password_hash != "IdenticalPassword123!"
    # Bcrypt generates unique salts per hash, so identical passwords produce different hashes
    assert u1.password_hash != u2.password_hash


def test_login_success(client: TestClient, db_session: Session):
    """Test successful login returns a valid JWT access token."""
    user = User(
        name="Sita Soren",
        email="sita.soren@solvesphere.jh",
        password_hash=get_password_hash("CorrectPassword123!"),
        role="faculty",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    login_payload = {
        "username": "sita.soren@solvesphere.jh",
        "password": "CorrectPassword123!",
    }
    response = client.post("/api/auth/login", data=login_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20


def test_login_wrong_password(client: TestClient, db_session: Session):
    """Test login with wrong password returns 401 Unauthorized."""
    user = User(
        name="Test User",
        email="testwrongpw@solvesphere.jh",
        password_hash=get_password_hash("Secret123!"),
        role="citizen",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": "testwrongpw@solvesphere.jh", "password": "WrongPassword!"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_nonexistent_user(client: TestClient):
    """Test login with an email that does not exist returns 401 Unauthorized."""
    response = client.post(
        "/api/auth/login",
        data={"username": "ghost@solvesphere.jh", "password": "AnyPassword123!"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_inactive_user(client: TestClient, db_session: Session):
    """Test login with a deactivated user returns 403 Forbidden."""
    inactive_user = User(
        name="Inactive Account",
        email="inactive@solvesphere.jh",
        password_hash=get_password_hash("ValidPassword123!"),
        role="citizen",
        is_active=False,
    )
    db_session.add(inactive_user)
    db_session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": "inactive@solvesphere.jh", "password": "ValidPassword123!"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "inactive" in response.json()["detail"].lower()



def test_auth_me_success(client: TestClient, db_session: Session):
    """Test GET /api/auth/me with valid JWT token returns profile."""
    user = User(
        name="Anjali Kumari",
        email="anjali.k@solvesphere.jh",
        password_hash=get_password_hash("Password123!"),
        role="university",
        phone="9988776655",
        preferred_language="en",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user.id
    assert data["name"] == "Anjali Kumari"
    assert data["email"] == "anjali.k@solvesphere.jh"
    assert data["role"] == "university"
    assert data["phone"] == "9988776655"
    assert data["preferred_language"] == "en"
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data


def test_auth_me_missing_jwt(client: TestClient):
    """Test GET /api/auth/me without token returns 401 Unauthorized."""
    response = client.get("/api/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "WWW-Authenticate" in response.headers


def test_auth_me_invalid_jwt(client: TestClient):
    """Test GET /api/auth/me with malformed or tampered token returns 401 Unauthorized."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid.fake.token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_auth_me_expired_jwt(client: TestClient, db_session: Session):
    """Test GET /api/auth/me with expired token returns 401 Unauthorized."""
    user = User(
        name="Expired User",
        email="expired@solvesphere.jh",
        password_hash=get_password_hash("Password123!"),
        role="citizen",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    expired_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(minutes=-10),  # expired 10 minutes ago
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "expired" in response.json()["detail"].lower()


def test_auth_me_inactive_user_with_token(client: TestClient, db_session: Session):
    """Test GET /api/auth/me for a deactivated user returns 400 Bad Request."""
    user = User(
        name="Disabled User",
        email="disabled@solvesphere.jh",
        password_hash=get_password_hash("Password123!"),
        role="citizen",
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "inactive" in response.json()["detail"].lower()


def test_role_authorization_single_role(client: TestClient, db_session: Session):
    """Test require_role allows authorized role and rejects unauthorized roles."""
    admin_user = User(
        name="Gov Officer",
        email="officer@jharkhand.gov.in",
        password_hash=get_password_hash("GovSecret123!"),
        role="government_admin",
        is_active=True,
    )
    citizen_user = User(
        name="Citizen Dev",
        email="citizendev@solvesphere.jh",
        password_hash=get_password_hash("CitizenSecret123!"),
        role="citizen",
        is_active=True,
    )
    db_session.add_all([admin_user, citizen_user])
    db_session.commit()
    db_session.refresh(admin_user)
    db_session.refresh(citizen_user)

    admin_token = create_access_token(data={"sub": str(admin_user.id)})
    citizen_token = create_access_token(data={"sub": str(citizen_user.id)})

    # Government Admin accessing admin-only endpoint -> 200 OK
    admin_resp = client.get(
        "/api/test-roles/admin-only",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_resp.status_code == status.HTTP_200_OK
    assert admin_resp.json()["role"] == "government_admin"

    # Citizen accessing admin-only endpoint -> 403 Forbidden
    citizen_resp = client.get(
        "/api/test-roles/admin-only",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert citizen_resp.status_code == status.HTTP_403_FORBIDDEN
    assert "Access forbidden" in citizen_resp.json()["detail"]


def test_role_authorization_multiple_roles(client: TestClient, db_session: Session):
    """Test require_role with multiple allowed roles (e.g., faculty or university)."""
    faculty_user = User(
        name="Prof. Sharma",
        email="sharma@bitmesra.ac.in",
        password_hash=get_password_hash("Prof123!"),
        role="faculty",
        is_active=True,
    )
    uni_user = User(
        name="Ranchi Univ Admin",
        email="admin@ranchiuniversity.ac.in",
        password_hash=get_password_hash("Uni123!"),
        role="university",
        is_active=True,
    )
    student_user = User(
        name="Rahul Kumar",
        email="rahul@student.ac.in",
        password_hash=get_password_hash("Student123!"),
        role="student",
        is_active=True,
    )
    db_session.add_all([faculty_user, uni_user, student_user])
    db_session.commit()
    db_session.refresh(faculty_user)
    db_session.refresh(uni_user)
    db_session.refresh(student_user)

    faculty_token = create_access_token(data={"sub": str(faculty_user.id)})
    uni_token = create_access_token(data={"sub": str(uni_user.id)})
    student_token = create_access_token(data={"sub": str(student_user.id)})

    # Faculty access to /api/test-roles/faculty-or-university -> 200 OK
    resp_faculty = client.get(
        "/api/test-roles/faculty-or-university",
        headers={"Authorization": f"Bearer {faculty_token}"},
    )
    assert resp_faculty.status_code == status.HTTP_200_OK

    # University access to /api/test-roles/faculty-or-university -> 200 OK
    resp_uni = client.get(
        "/api/test-roles/faculty-or-university",
        headers={"Authorization": f"Bearer {uni_token}"},
    )
    assert resp_uni.status_code == status.HTTP_200_OK

    # Student access to /api/test-roles/faculty-or-university -> 403 Forbidden
    resp_student = client.get(
        "/api/test-roles/faculty-or-university",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp_student.status_code == status.HTTP_403_FORBIDDEN
