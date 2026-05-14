# SkyDeck API

**Aviation Safety System MVP** — FastAPI backend with JWT authentication, session management, manual library with forensic watermarking, digital form submissions, and multi-tenant org support.

| Stack | Version |
|-------|---------|
| Python | 3.9+ |
| FastAPI | 0.115 |
| SQLAlchemy | 2.0 (sync) |
| PostgreSQL | 16 |
| Alembic | 1.14 |
| Auth | JWT (HS256) via python-jose |
| PDF Engine | pypdf + reportlab |

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Structure](#project-structure)
3. [Testing the API](#testing-the-api)
4. [API Reference — Auth](#api-reference--auth)
5. [API Reference — Manuals](#api-reference--manuals)
6. [API Reference — Forms & Submissions](#api-reference--forms--submissions)
7. [Running Tests](#running-tests)
8. [Architecture Docs](#architecture-docs)
9. [Environment Variables](#environment-variables)

---

## Quick Start

### Prerequisites

- Python 3.9 or later
- PostgreSQL 16 running on `localhost:5432` (via Docker or local install)
- Database created with credentials matching your `.env` file

### 1. Clone and configure

```powershell
git clone https://gitlab.com/skyhightech_efb/efb-backend.git skydeck
cd skydeck
cp .env.example .env        # edit credentials if needed
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Launch the server

```powershell
.\start_server.ps1
```

### 4. Run migrations and seed (first time only)

```powershell
python -m alembic upgrade head
python -m app.seed
```

The seed creates a demo organisation, 5 users, manuals, forms, and submissions. The default admin login is:

| Field | Value |
|-------|-------|
| Email | `s.mitchell@skywest-air.com` |
| Password | `SkyDeck@2026!` |

---

## Project Structure

```
skydeck/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── core/
│   │   ├── config.py            # pydantic-settings configuration
│   │   ├── security.py          # JWT, bcrypt, SHA-256 helpers
│   │   ├── deps.py              # get_current_user, require_roles
│   │   └── errors.py            # AppError hierarchy + handlers
│   ├── api/v1/
│   │   ├── auth.py              # POST signup / login / refresh / logout
│   │   ├── users.py             # GET /me
│   │   ├── manuals.py           # Upload / list / download / delete
│   │   ├── forms.py             # GET /forms/active
│   │   └── submissions.py       # POST / GET / GET /{id}
│   ├── models/                  # SQLAlchemy ORM models
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── repositories/            # Data-access layer
│   ├── services/
│   │   ├── auth_service.py      # Authentication business logic
│   │   ├── audit_service.py     # Centralised audit logging
│   │   ├── storage.py           # StorageProvider ABC + LocalStorage
│   │   └── watermark_service.py # PDF watermarking engine
│   ├── db/
│   │   ├── base.py              # Declarative Base
│   │   ├── session.py           # Engine + SessionLocal + get_db
│   │   └── types.py             # CIText custom type
│   └── seed.py                  # Database seeder
├── alembic/                     # Migration scripts
├── tests/                       # Pytest test suite
├── docs/                        # Architecture documentation
├── requirements.txt
├── pyproject.toml               # Ruff + Pytest config
├── Dockerfile                   # Multi-stage production build
├── docker-entrypoint.sh
├── start_server.ps1             # Local dev launcher
├── .env.example
└── .gitlab-ci.yml               # CI pipeline
```

---

## Testing the API

Open **http://127.0.0.1:8000/docs** in your browser to see the Swagger UI.

### Quick workflow

1. **Login:** `POST /api/v1/auth/login` with admin credentials
2. **Authorize:** Click padlock, paste `access_token`
3. **Test:** `GET /api/v1/users/me`, `GET /api/v1/manuals`, etc.

---

## API Reference — Auth

### `POST /api/v1/auth/signup`

Register a new pilot account (defaults to `pilot` role).

**Request body:**

```json
{
  "name": "Ali",
  "email": "ali@test.com",
  "password": "123456"
}
```

**Response `201`:**

```json
{
  "user_id": 12,
  "access_token": "...",
  "refresh_token": "..."
}
```

| Error | When |
|---|---|
| `409` | Email already registered |

### `POST /api/v1/auth/login`

**Request body:**

```json
{
  "email": "user@mail.com",
  "password": "123456",
  "device_info": {"platform": "iPad"}
}
```

**Response `200`:**

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {"id": 1, "name": "Ali", "role": "pilot"}
}
```

### `POST /api/v1/auth/refresh`

**Request:** `{"refresh_token": "..."}`
**Response `200`:** `{"access_token": "...", "token_type": "bearer"}`

### `POST /api/v1/auth/logout`

**Request:** `{"refresh_token": "..."}`
**Response `200`:** `{"message": "Logged out successfully"}`

### `GET /api/v1/users/me`

**Response `200`:**

```json
{
  "id": 1, "org_id": 1, "name": "Ali",
  "email": "ali@test.com", "role": "pilot",
  "created_at": "2026-01-01T00:00:00+00:00"
}
```

---

## API Reference — Manuals

### `POST /api/v1/manuals/upload` (Admin)

Upload a PDF manual via multipart/form-data.

| Field | Type | Required |
|---|---|---|
| `title` | string (form) | Yes |
| `file` | file (PDF) | Yes |

**Validation pipeline:** Size limit (50 MB) → Magic bytes (`%PDF-`) → SHA-256 dedup → Secure filename → Transaction-safe write.

**Response `201`:**

```json
{
  "id": 5, "title": "...", "original_filename": "...",
  "file_size": 2048576, "sha256": "a1b2c3..."
}
```

| Error | Code | When |
|---|---|---|
| Duplicate file | 409 | Same SHA-256 already exists |
| Too large | 413 | Exceeds MAX_UPLOAD_SIZE_MB |
| Not a PDF | 415 | Magic bytes check failed |
| Disk failure | 500 | StorageProvider.save() failed, DB rolled back |

### `GET /api/v1/manuals`

List active manuals for the user's org.

**Response `200`:** Array of manual objects.

### `GET /api/v1/manuals/{id}/download`

Download with server-side forensic watermark (CONFIDENTIAL + user name + timestamp + hash).

**Response `200`:** PDF binary stream with `X-Watermark-Hash` header.

### `DELETE /api/v1/manuals/{id}` (Admin)

Soft-delete and remove physical file.

**Response `200`:** `{"message": "Manual deleted successfully"}`

---

## API Reference — Forms & Submissions

### `GET /api/v1/forms/active`

Returns the latest version of each form template for the user's org.

**Response `200`:**

```json
[
  {
    "form_id": 1,
    "template_name": "Pre-Flight Inspection Report",
    "version": 2,
    "fields": [
      {"name": "flight_no", "type": "text", "required": true},
      {"name": "description", "type": "textarea"}
    ],
    "created_at": "2026-01-01T00:00:00+00:00"
  }
]
```

### `POST /api/v1/submissions` (Pilot/Admin)

Submit a form. Optional file attachment.

**Request:** multipart/form-data

| Field | Type | Required |
|---|---|---|
| `form_version_id` | int | Yes |
| `data` | string (JSON) | Yes |
| `file` | file | No |

**Response `201`:**

```json
{
  "submission_id": 55,
  "hash_id": "ABC123XYZ...",
  "status": "submitted"
}
```

### `GET /api/v1/submissions` (Admin/Viewer)

Paginated listing. Query: `?page=1&limit=20`

**Response `200`:**

```json
{
  "page": 1,
  "limit": 20,
  "total": 25,
  "items": [{"id": 1, "hash_id": "...", "status": "submitted", ...}]
}
```

### `GET /api/v1/submissions/{id}` (Admin/Viewer)

Full submission detail with attachments.

---

## Running Tests

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest tests/ -v
```

---

## Architecture Docs

| Document | Contents |
|----------|----------|
| [`docs/auth_architecture.md`](docs/auth_architecture.md) | Auth flow diagrams, token lifecycle, session management, cryptographic choices |
| [`docs/manual_architecture.md`](docs/manual_architecture.md) | Manual library flows, transaction rollback, storage abstraction, watermarking engine, magic bytes validation, audit logging |
| [`docs/forms_submissions_architecture.md`](docs/forms_submissions_architecture.md) | Forms & submissions flows, RBAC, data dictionary |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `skydeck` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `skydeck` | PostgreSQL password |
| `POSTGRES_DB` | `skydeck` | Database name |
| `POSTGRES_SERVER` | `localhost` | Database hostname |
| `POSTGRES_PORT` | `5432` | Database port |
| `DATABASE_URL` | *(assembled)* | Full connection string override |
| `SECRET_KEY` | *(change me)* | JWT signing key |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `STORAGE_DIR` | `storage/manuals` | Manual PDF storage directory |
| `SUBMISSIONS_STORAGE_DIR` | `storage/submissions` | Submission attachment storage |
| `MAX_UPLOAD_SIZE_MB` | `50` | Maximum upload file size |
| `WATERMARK_FONT_SIZE` | `40` | Watermark text size (pt) |
| `BACKEND_PORT` | `8000` | Uvicorn listen port |
| `RUN_SEED` | `false` | Auto-seed on container start |
