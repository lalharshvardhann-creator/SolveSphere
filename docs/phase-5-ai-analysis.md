# SolveSphere Phase 5B — Gemini AI Challenge Analysis Documentation

This document describes the architecture, data structures, error handling, security practices, and verification procedures for the Google Gemini AI Analysis subsystem in SolveSphere.

---

## 1. Overview & Architecture

SolveSphere leverages Google's Gemini models via the official `google-genai` SDK to perform automated, structured analysis of submitted societal challenges in Jharkhand.

```
+-----------------------------------------------------------------------------------+
|                                SolveSphere Flow                                   |
|                                                                                   |
|  Challenge In DB  ───>  AIAnalysisService  ───>  GeminiService (google-genai)    |
|       │                        │                              │                   |
|       │                        │                              ▼                   |
|       │                        │                     Gemini API (JSON Mode)       |
|       │                        │                              │                   |
|       │                        ▼                              ▼                   |
|       │                 Upsert Record  <───  Validated Structured Response        |
|       │                        │            (ChallengeAIAnalysisStructured)       |
|       ▼                        ▼                                                  |
|  Updated Priority   challenge_ai_analysis table                                   |
+-----------------------------------------------------------------------------------+
```

### Key Architectural Principles
- **PostgreSQL as Single Source of Truth**: All AI analytical findings are validated and persisted to the relational `challenge_ai_analysis` table.
- **Dedicated Service Isolation**: Direct Gemini communication is encapsulated in `GeminiService` (`app.services.gemini_service`), keeping business logic separated in `AIAnalysisService`.
- **Strict Schema Validation**: Gemini output is forced into JSON mode with strict Pydantic model validation (`ChallengeAIAnalysisStructured`). Unstructured or malformed outputs are rejected before persistence.
- **Explicit Triggering**: AI analysis is triggered on demand via an authenticated API endpoint (`POST /api/challenges/{challenge_id}/analyze`), avoiding unnecessary quota usage.

---

## 2. Gemini Integration & Structured Schema

### 1. Gemini Client Initialization
The client is instantiated on-demand using the active `settings.GEMINI_API_KEY`:
```python
from google import genai
from google.genai import types

client = genai.Client(api_key=settings.GEMINI_API_KEY)
```

### 2. Structured Pydantic Output Model
```python
class ChallengeAIAnalysisStructured(BaseModel):
    problem_summary: str
    detected_category: str
    detected_subcategory: Optional[str] = None
    priority_score: float  # Range: 1.0 to 10.0
    relevant_keywords: List[str]
    suggested_solution_directions: List[str]
    confidence_score: float  # Range: 0.0 to 1.0
```

### 3. Database Mapping (`challenge_ai_analysis` table)
| Database Column | Source from Structured Output | Description |
| :--- | :--- | :--- |
| `challenge_id` | `challenge.id` | Foreign key referencing the analyzed challenge |
| `category` | `detected_category` | Core domain classification |
| `subcategory` | `detected_subcategory` | Sub-domain categorization |
| `keywords` | `", ".join(relevant_keywords)` | Comma-separated keyword list |
| `priority_score` | `priority_score` | Urgency rating (1.0 - 10.0) |
| `required_expertise` | `"; ".join(suggested_solution_directions)` | Recommended research/engineering directions |
| `model_version` | `settings.GEMINI_MODEL` | Gemini model version identifier (`gemini-2.5-flash`) |
| `created_at` | UTC timestamp | Creation/last updated timestamp |

---

## 3. API Endpoints Reference

### 1. Trigger AI Analysis
- **Method**: `POST`
- **Path**: `/api/challenges/{challenge_id}/analyze`
- **Authentication**: Required (`Bearer <JWT>`)
- **Success Response (`200 OK`)**:
  ```json
  {
    "id": 1,
    "challenge_id": 42,
    "category": "Water Supply",
    "subcategory": "Groundwater Contamination",
    "keywords": "arsenic, groundwater, filtration, ranchi, water safety",
    "priority_score": 8.5,
    "duplicate_score": null,
    "required_expertise": "Deploy modular adsorption filtration units; Implement community IoT water quality sensing",
    "model_version": "gemini-2.5-flash",
    "created_at": "2026-09-08T15:10:00Z",
    "problem_summary": "Arsenic contamination in drinking groundwater exceeding safety levels in rural Ranchi.",
    "confidence_score": 0.94
  }
  ```

### 2. Retrieve Stored AI Analysis
- **Method**: `GET`
- **Path**: `/api/challenges/{challenge_id}/ai-analysis`
- **Authentication**: Public / Read
- **Success Response (`200 OK`)**:
  ```json
  {
    "id": 1,
    "challenge_id": 42,
    "category": "Water Supply",
    "subcategory": "Groundwater Contamination",
    "keywords": "arsenic, groundwater, filtration, ranchi, water safety",
    "priority_score": 8.5,
    "duplicate_score": null,
    "required_expertise": "Deploy modular adsorption filtration units; Implement community IoT water quality sensing",
    "model_version": "gemini-2.5-flash",
    "created_at": "2026-09-08T15:10:00Z"
  }
  ```

---

## 4. Security & Safety Practices

1. **Zero Hardcoded Secrets**: `GEMINI_API_KEY` is loaded exclusively via `pydantic-settings` from `backend/.env`.
2. **API Key Concealment**: The API key is never serialized in response models, debug logs, error messages, or Git history.
3. **Re-Analysis Upsert Safety**: Triggering analysis multiple times on the same challenge updates the existing record cleanly without duplicate key violations.
4. **Resilient Failure Handling**:
   - `503 Service Unavailable`: When `GEMINI_API_KEY` is missing or blank.
   - `502 Bad Gateway`: When Gemini API encounters rate limits, network timeouts, or invalid JSON.
   - `404 Not Found`: When the requested `challenge_id` does not exist.
   - `401 Unauthorized`: When an unauthenticated user attempts to trigger analysis.

---

## 5. Automated Testing

All automated tests use unittest mocks to avoid consuming live Gemini quota and ensure deterministic test runs:

```bash
cd backend
python -m pytest -v
```

### Coverage
- `test_analyze_challenge_success_mocked`: Validates prompt execution, schema parsing, and DB upsert.
- `test_analyze_challenge_reanalysis_upsert`: Validates idempotent updates.
- `test_analyze_challenge_malformed_response`: Tests 502 handling on invalid JSON.
- `test_analyze_challenge_gemini_api_exception`: Tests 502 handling on SDK exceptions.
- `test_analyze_challenge_missing_api_key`: Tests 503 handling when key is not configured.
- `test_analyze_challenge_not_found`: Tests 404 handling.
- `test_analyze_challenge_unauthenticated`: Tests 401 handling.
- `test_get_ai_analysis_endpoint`: Tests GET endpoint for stored analysis.

---

## 6. Manual Verification with Real Gemini API

To test against live Google Gemini endpoints locally:

1. Obtain a valid Gemini API key from [Google AI Studio](https://aistudio.google.com/).
2. Add your key to `backend/.env`:
   ```env
   GEMINI_API_KEY=AIzaSyYourActualKeyHere
   ```
3. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
4. Register & Log in to get an access token:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"birsa@solvesphere.jh","password":"SecurePassword123!"}'
   ```
5. Trigger AI Analysis for a challenge (e.g. ID 1):
   ```bash
   curl -X POST http://localhost:8000/api/challenges/1/analyze \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
   ```
6. Check stored analysis:
   ```bash
   curl -X GET http://localhost:8000/api/challenges/1/ai-analysis
   ```
