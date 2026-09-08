# SolveSphere Phase 4 — Authentication & Role Management Documentation

This document outlines the architecture, security mechanisms, API contracts, role authorization patterns, and testing guidelines for the SolveSphere authentication foundation.

---

## 1. Overview & Architecture

SolveSphere enforces a secure, token-based authentication system built with **FastAPI**, **SQLAlchemy**, **Bcrypt**, and **PyJWT**.

- **Password Security**: Passwords are never stored in plaintext. They are salted and hashed using `bcrypt`.
- **Stateless Authentication**: Access tokens are signed JSON Web Tokens (`JWT` using `HS256`) containing user claims (`sub`, `email`, `role`, `iat`, `exp`).
- **Configuration Security**: JWT secret keys, algorithms, and expiration intervals are managed via environment variables (`JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`). Secrets are never committed to version control.
- **Privacy & Safety**: Passwords and password hashes are strictly filtered out of all API responses.

---

## 2. Supported Roles

SolveSphere defines six distinct user roles within the platform:

| Role Name | Description |
| :--- | :--- |
| `citizen` | Residents submitting societal challenges and local issues. |
| `university` | Higher Education Institutions (HEIs) and college administrative bodies. |
| `faculty` | University professors, researchers, and academic subject-matter experts. |
| `student` | University/college students working on solutions, projects, and hackathons. |
| `industry` | Corporate, MSME, or industrial innovation and funding partners. |
| `government_admin` | State officials and system administrators managing approvals and oversight. |

Role definitions are located in `app.core.roles.UserRole` and `VALID_ROLES`.

---

## 3. Authentication & JWT Flow

```
1. Registration:
   Client ──(POST /api/auth/register)──> Server (Validates role, checks unique email, hashes password)
                                       ──> DB (Saves User record)
                                       <── Returns safe user profile (201 Created)

2. Login:
   Client ──(POST /api/auth/login)───> Server (Checks credentials & active account status)
                                       <── Returns JWT access token (200 OK)

3. Authenticated Request:
   Client ──(GET /api/auth/me)────────> Server (Decodes JWT, verifies signature & expiry, loads active user)
             Authorization: Bearer <token>
                                       <── Returns authenticated user profile (200 OK)
```

---

## 4. API Endpoints Reference

### 1. Register User
- **Endpoint**: `POST /api/auth/register`
- **Status Code**: `201 Created`
- **Request Body**:
  ```json
  {
    "name": "Birsa Munda",
    "email": "birsa@solvesphere.jh",
    "password": "SecurePassword123!",
    "role": "citizen",
    "phone": "9876543210",
    "preferred_language": "hi"
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "name": "Birsa Munda",
    "email": "birsa@solvesphere.jh",
    "role": "citizen",
    "phone": "9876543210",
    "preferred_language": "hi",
    "is_active": true,
    "created_at": "2026-09-08T14:40:00Z",
    "updated_at": "2026-09-08T14:40:00Z"
  }
  ```

---

### 2. Login
- **Endpoint**: `POST /api/auth/login`
- **Status Code**: `200 OK`
- **Request Body**:
  ```json
  {
    "email": "birsa@solvesphere.jh",
    "password": "SecurePassword123!"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

---

### 3. Get Current User Profile
- **Endpoint**: `GET /api/auth/me`
- **Status Code**: `200 OK`
- **Headers**:
  ```
  Authorization: Bearer <access_token>
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "name": "Birsa Munda",
    "email": "birsa@solvesphere.jh",
    "role": "citizen",
    "phone": "9876543210",
    "preferred_language": "hi",
    "is_active": true,
    "created_at": "2026-09-08T14:40:00Z",
    "updated_at": "2026-09-08T14:40:00Z"
  }
  ```

---

## 5. Role-Based Authorization Guard

SolveSphere provides a reusable dependency factory: `require_role(*allowed_roles)` in `app.api.deps`.

### Single Role Guard:
```python
from fastapi import APIRouter, Depends
from app.api.deps import require_role
from app.models.user import User

router = APIRouter()

@router.post("/admin/verify-institution")
def verify_institution(
    admin_user: User = Depends(require_role("government_admin")),
):
    return {"message": "Verified by admin", "admin": admin_user.name}
```

### Multiple Role Guard:
```python
@router.post("/projects/create")
def create_project(
    creator: User = Depends(require_role("faculty", "university")),
):
    return {"message": "Project created", "creator_role": creator.role}
```

If an unauthenticated or unauthorized user attempts to access the route, FastAPI automatically returns:
- `401 Unauthorized` for missing/invalid/expired token.
- `403 Forbidden` for insufficient role permissions (`Access forbidden: requires one of the following roles: ...`).

---

## 6. How to Test Locally

### Running Automated Tests
Run pytest in the backend virtual environment:
```bash
cd backend
python -m pytest -v
```

### Manual Testing with cURL

#### 1. Register a new user:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Sunita Murmu","email":"sunita@example.com","password":"Password123!","role":"student"}'
```

#### 2. Log in and get JWT token:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"sunita@example.com","password":"Password123!"}'
```

#### 3. Access current user profile:
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <TOKEN_RECEIVED_FROM_LOGIN>"
```
