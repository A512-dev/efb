# SkyDeck API

**Aviation Safety System MVP** — FastAPI backend with JWT authentication, session management, manual library with forensic watermarking, digital form submissions, internal pilot/admin messaging, audit logging, and multi-tenant org support.

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

1. [Repository Layout](#repository-layout)
2. [Current Progress](#current-progress)
3. [Quick Start — Backend](#quick-start--backend)
4. [Quick Start — Frontend](#quick-start--frontend)
5. [Database, PostgreSQL, and Schema Viewing](#database-postgresql-and-schema-viewing)
6. [Default Seed Users](#default-seed-users)
7. [Project Structure](#project-structure)
8. [Testing the API](#testing-the-api)
9. [API Reference — Auth](#api-reference--auth)
10. [API Reference — Manuals](#api-reference--manuals)
11. [API Reference — Forms & Submissions](#api-reference--forms--submissions)
12. [API Reference — Messages](#api-reference--messages)
13. [Running Tests](#running-tests)
14. [Architecture Docs](#architecture-docs)
15. [Environment Variables](#environment-variables)
16. [Development Workflow](#development-workflow)

---

## Repository Layout

This repository currently contains both the frontend and backend:

```text
program/
├── package.json              # Frontend dependencies/scripts
├── package-lock.json
├── vite.config.js            # Frontend dev proxy to backend
├── src/                      # React frontend
└── skydeck/                  # FastAPI backend
    ├── app/
    ├── alembic/
    ├── deploy-assets/
    ├── requirements.txt
    └── README.md
```

The frontend is a **Vite React** app at the repository root.

The backend is the **FastAPI** app inside `skydeck/`.

---

## Current Progress

### Backend features already present

- JWT signup/login/refresh/logout
- Access token and refresh token system
- Server-side session tracking in `sessions`
- Password hashing with bcrypt
- Refresh-token hashing with SHA-256
- Role-based route protection
- PostgreSQL schema managed through Alembic
- Manual upload/list/download/delete
- PDF validation and SHA-256 deduplication
- Forensic PDF watermarking with `pypdf` and `reportlab`
- Digital form templates and versioned form schemas
- Digital form submissions with optional attachments
- Central audit logging through `audit_logs`
- Seed script with demo org/users/forms/manuals/submissions

### Message feature added during current backend handoff

A new internal messaging backend was added for the frontend message tab / `IranAirChat` screen.

New files:

```text
app/models/message.py
app/schemas/message.py
app/repositories/message_repo.py
app/api/v1/messages.py
alembic/versions/0002_add_messages.py
```

Updated files:

```text
app/models/__init__.py
app/repositories/user_repo.py
app/main.py
```

New table:

```text
messages
```

New endpoints:

```text
POST /api/v1/messages
GET  /api/v1/messages
POST /api/v1/messages/{message_id}/read
```

Implemented message rules:

| Sender | Recipient Rule |
|--------|----------------|
| `pilot` | Sends to all admins in the same organisation. |
| `chief_pilot` | Sends to all admins in the same organisation. |
| `admin` | Sends to selected `pilot` or `chief_pilot` users by `recipient_ids`. |
| `safety`, `planning`, `technical` | Not allowed to send messages yet. |

### Frontend status discovered

The frontend has a message tab at:

```text
src/pages/IranAirChat.jsx
```

At the time of backend review, it was still a placeholder UI: it displayed a textarea and an alert, but did not call the backend or load real messages.

Frontend still needs to be wired to:

```text
POST /api/v1/messages
GET  /api/v1/messages
POST /api/v1/messages/{message_id}/read
```

### Known frontend cleanup item

Some JSX uses `class` instead of `className`, which causes React warnings such as:

```text
Invalid DOM property `class`. Did you mean `className`?
```

Example area: `IranAirChat.jsx`.

This warning is not a backend/login blocker, but should be cleaned up.

---

## Quick Start — Backend

### Prerequisites

- Python 3.9 or later
- PostgreSQL 16, either through Docker or a local Windows PostgreSQL install
- A `.env` file inside `skydeck/`

### 1. Go to the backend folder

```powershell
cd E:\work\efb\program\skydeck
```

### 2. Create `.env`

```powershell
Copy-Item .env.example .env
```

For local development, the default values are usually fine:

```env
POSTGRES_USER=skydeck
POSTGRES_PASSWORD=skydeck
POSTGRES_DB=skydeck
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
APP_NAME=SkyDeck
DEBUG=true
BACKEND_PORT=8000
SECRET_KEY=CHANGE-ME-generate-a-64-byte-random-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
RUN_SEED=true
```

Production must use a real secret key. Do not deploy with the default `CHANGE-ME...` value.

### 3. Create and activate Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Install backend dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5A. Start PostgreSQL with Docker

If Docker Desktop is installed and running:

```powershell
docker compose -f deploy-assets/docker-compose.yml up -d db pgadmin
```

This starts:

| Service | URL / Port |
|---------|------------|
| PostgreSQL | `localhost:5432` |
| pgAdmin | `http://localhost:5050` |

### 5B. Or use local PostgreSQL without Docker

If PostgreSQL is installed directly on Windows, create the user and database manually:

```sql
CREATE USER skydeck WITH PASSWORD 'skydeck';
CREATE DATABASE skydeck OWNER skydeck;
GRANT ALL PRIVILEGES ON DATABASE skydeck TO skydeck;
```

Then make sure `.env` points to:

```env
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=skydeck
POSTGRES_PASSWORD=skydeck
POSTGRES_DB=skydeck
```

### 6. Run migrations

```powershell
python -m alembic upgrade head
```

This creates all database tables, including:

```text
orgs
users
sessions
login_attempts
manuals
manual_access_logs
form_templates
form_versions
submissions
submission_attachments
audit_logs
messages
```

### 7. Seed demo data

```powershell
python -m app.seed
```

The seed creates a demo organisation, users, manuals, form templates, form versions, submissions, and audit data.

Important: the seed script skips if the database already has organisations:

```text
[seed] Database already contains data — skipping.
```

If login fails with the default users, verify that the users actually exist in the current database.

### 8. Start backend server

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Or use the included PowerShell launcher:

```powershell
.\start_server.ps1
```

Backend URLs:

| Page | URL |
|------|-----|
| Swagger UI | `http://127.0.0.1:8000/docs` |
| ReDoc | `http://127.0.0.1:8000/redoc` |
| Health check | `http://127.0.0.1:8000/health` |

---

## Quick Start — Frontend

Open a second terminal and go to the repository root:

```powershell
cd E:\work\efb\program
```

Install dependencies:

```powershell
npm install
```

Start Vite:

```powershell
npm run dev
```

Open the frontend URL shown by Vite, usually:

```text
http://localhost:5173
```

The frontend calls the backend through `/api`.

`vite.config.js` proxies `/api` to:

```text
http://127.0.0.1:8000
```

So this frontend request:

```text
/api/v1/auth/login
```

is forwarded to:

```text
http://127.0.0.1:8000/api/v1/auth/login
```

---

## Database, PostgreSQL, and Schema Viewing

### Where is the database stored?

The project does **not** store PostgreSQL data inside `app/db/`.

This folder:

```text
skydeck/app/db/
```

only contains Python code for connecting to PostgreSQL.

If using Docker, PostgreSQL stores its data in a Docker volume:

```yaml
volumes:
  pgdata:
```

If using local PostgreSQL, data is stored wherever the Windows PostgreSQL installation stores its database files.

### How tables are created

Tables are created by Alembic migrations:

```powershell
python -m alembic upgrade head
```

Migration files live in:

```text
skydeck/alembic/versions/
```

Current migrations:

```text
0001_initial_schema.py      # initial auth/manual/forms/submissions schema
0002_add_messages.py        # internal messaging table and indexes
```

### View schema with pgAdmin

If using Docker compose:

```powershell
docker compose -f deploy-assets/docker-compose.yml up -d db pgadmin
```

Open:

```text
http://localhost:5050
```

Default pgAdmin login:

| Field | Value |
|-------|-------|
| Email | `admin@skydeck.local` |
| Password | `admin` |

Add a server in pgAdmin:

| Field | Value |
|-------|-------|
| Host | `db` |
| Port | `5432` |
| Username | `skydeck` |
| Password | `skydeck` |
| Database | `skydeck` |

### View schema with psql

If using Docker:

```powershell
docker compose -f deploy-assets/docker-compose.yml exec db psql -U skydeck -d skydeck
```

Useful commands:

```sql
\dt
\d users
\d messages
\d submissions
\d manuals
```

### View schema with DBeaver / TablePlus / DataGrip

Use:

| Field | Value |
|-------|-------|
| Host | `localhost` |
| Port | `5432` |
| Database | `skydeck` |
| Username | `skydeck` |
| Password | `skydeck` |

---

## Default Seed Users

All seeded users use this password:

```text
SkyDeck@2026!
```

| Role | Name | Email | Password |
|------|------|-------|----------|
| admin | Sarah Mitchell | `s.mitchell@skywest-air.com` | `SkyDeck@2026!` |
| chief_pilot | Captain James Thornton | `j.thornton@skywest-air.com` | `SkyDeck@2026!` |
| pilot | First Officer Ava Chen | `a.chen@skywest-air.com` | `SkyDeck@2026!` |
| pilot | First Officer Marcus Rivera | `m.rivera@skywest-air.com` | `SkyDeck@2026!` |
| pilot | Captain Nadia Okonkwo | `n.okonkwo@skywest-air.com` | `SkyDeck@2026!` |

To verify users in the current database:

```powershell
python -c "from app.db.session import SessionLocal; from app.models.user import User; db=SessionLocal(); [print(u.id, u.email, u.name, u.role) for u in db.query(User).all()]; db.close()"
```

If users are missing and this is only local/dev data, reset the Docker database:

```powershell
docker compose -f deploy-assets/docker-compose.yml down -v
docker compose -f deploy-assets/docker-compose.yml up -d db pgadmin
python -m alembic upgrade head
python -m app.seed
```

---

## Project Structure

```text
skydeck/
├── app/
│   ├── main.py                  # FastAPI entry point and router registration
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
│   │   ├── submissions.py       # POST / GET / GET /{id}
│   │   └── messages.py          # Send/list/read internal pilot-admin messages
│   ├── models/                  # SQLAlchemy ORM models / database tables
│   │   ├── user.py
│   │   ├── org.py
│   │   ├── manual.py
│   │   ├── form_template.py
│   │   ├── form_version.py
│   │   ├── submission.py
│   │   ├── message.py           # messages table
│   │   └── ...
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── manual.py
│   │   ├── submission.py
│   │   ├── message.py           # message request/response schemas
│   │   └── ...
│   ├── repositories/            # Data-access layer
│   │   ├── user_repo.py
│   │   ├── manual_repo.py
│   │   ├── submission_repo.py
│   │   ├── message_repo.py      # message queries and persistence
│   │   └── ...
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
├── alembic/
│   └── versions/
│       ├── 0001_initial_schema.py
│       └── 0002_add_messages.py
├── tests/                       # Pytest test suite
├── docs/                        # Architecture documentation
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml               # Ruff + Pytest config
├── Dockerfile                   # Multi-stage production build
├── docker-entrypoint.sh
├── start_server.ps1             # Local dev launcher
├── deploy-assets/
│   └── docker-compose.yml       # Local DB/pgAdmin/backend compose
├── .env.example
└── .gitlab-ci.yml               # CI pipeline
```

---

## Testing the API

Open:

```text
http://127.0.0.1:8000/docs
```

### Quick workflow

1. Login through `POST /api/v1/auth/login` with seeded credentials.
2. Copy the returned `access_token`.
3. Click **Authorize** in Swagger.
4. Paste the token as the bearer token.
5. Test endpoints like:
   - `GET /api/v1/users/me`
   - `GET /api/v1/manuals`
   - `GET /api/v1/forms/active`
   - `GET /api/v1/messages`

Example login body:

```json
{
  "email": "s.mitchell@skywest-air.com",
  "password": "SkyDeck@2026!",
  "device_info": {
    "platform": "Web"
  }
}
```

---

## API Reference — Auth

### `POST /api/v1/auth/signup`

Register a new pilot account. New users default to the `pilot` role.

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

Authenticate and receive access/refresh tokens.

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

**Request:**

```json
{"refresh_token": "..."}
```

**Response `200`:**

```json
{"access_token": "...", "token_type": "bearer"}
```

### `POST /api/v1/auth/logout`

**Request:**

```json
{"refresh_token": "..."}
```

**Response `200`:**

```json
{"message": "Logged out successfully"}
```

### `GET /api/v1/users/me`

Returns the current authenticated user profile.

**Response `200`:**

```json
{
  "id": 1,
  "org_id": 1,
  "name": "Ali",
  "email": "ali@test.com",
  "role": "pilot",
  "created_at": "2026-01-01T00:00:00+00:00"
}
```

---

## API Reference — Manuals

### `POST /api/v1/manuals/upload` (Admin)

Upload a PDF manual via multipart/form-data.

| Field | Type | Required |
|---|---|---|
| `title` | string form field | Yes |
| `file` | PDF file | Yes |

Validation pipeline:

```text
size limit -> PDF magic bytes -> SHA-256 dedup -> secure filename -> storage write -> audit log
```

**Response `201`:**

```json
{
  "id": 5,
  "title": "...",
  "original_filename": "...",
  "file_size": 2048576,
  "sha256": "a1b2c3...",
  "message": "Manual uploaded successfully"
}
```

| Error | Code | When |
|---|---|---|
| Duplicate file | 409 | Same SHA-256 already exists |
| Too large | 413 | Exceeds `MAX_UPLOAD_SIZE_MB` |
| Not a PDF | 415 | Magic bytes check failed |
| Disk failure | 500 | `StorageProvider.save()` failed, DB rolled back |

### `GET /api/v1/manuals`

List active manuals for the user's organisation.

**Response `200`:** array of manual objects.

### `GET /api/v1/manuals/{id}/download`

Download with server-side forensic watermark:

```text
CONFIDENTIAL + user name + timestamp + watermark hash
```

**Response `200`:** PDF binary stream with `X-Watermark-Hash` response header.

### `DELETE /api/v1/manuals/{id}` (Admin)

Soft-delete the DB record and remove the physical file.

**Response `200`:**

```json
{"message": "Manual deleted successfully"}
```

---

## API Reference — Forms & Submissions

### `GET /api/v1/forms/active`

Returns the latest version of each form template for the user's organisation.

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

### `POST /api/v1/submissions` (Pilot/Admin/Chief Pilot)

Submit a form. Optional file attachment.

**Request:** multipart/form-data

| Field | Type | Required |
|---|---|---|
| `form_version_id` | int | Yes |
| `data` | string JSON object | Yes |
| `file` | file | No |

**Response `201`:**

```json
{
  "submission_id": 55,
  "hash_id": "ABC123XYZ...",
  "status": "submitted"
}
```

### `GET /api/v1/submissions` (Admin/Viewer Roles)

Paginated listing. Query params:

```text
?page=1&limit=20
```

**Response `200`:**

```json
{
  "page": 1,
  "limit": 20,
  "total": 25,
  "items": [
    {"id": 1, "hash_id": "...", "status": "submitted"}
  ]
}
```

### `GET /api/v1/submissions/{id}` (Admin/Viewer Roles)

Full submission detail with attachments.

---

## API Reference — Messages

The message module supports the frontend `IranAirChat` tab.

Current business rules:

| Sender | Recipient Rule |
|--------|----------------|
| `pilot` | Sends to all admins in the same organisation. Pilot does not choose recipients. |
| `chief_pilot` | Sends to all admins in the same organisation. Chief pilot does not choose recipients. |
| `admin` | Sends to selected `pilot` or `chief_pilot` users by `recipient_ids`. |
| `safety`, `planning`, `technical` | Not allowed to send messages in the current implementation. |

Every message is stored in the `messages` table and every send/read action is written to `audit_logs`.

### `POST /api/v1/messages`

Send an internal message.

#### Pilot / chief pilot request

Pilots do not provide `recipient_ids`:

```json
{
  "subject": "Issue report",
  "body": "There is a problem with the checklist PDF."
}
```

This creates one message per admin in the same organisation.

#### Admin request

Admins must provide selected pilot/chief pilot recipient IDs:

```json
{
  "subject": "Response to your issue",
  "body": "Thanks, I checked it. Please use the updated document.",
  "recipient_ids": [3, 4]
}
```

**Response `201`:**

```json
{
  "message": "Message sent successfully",
  "items": [
    {
      "id": 1,
      "org_id": 1,
      "sender_id": 1,
      "recipient_id": 3,
      "subject": "Response to your issue",
      "body": "Thanks, I checked it. Please use the updated document.",
      "read_at": null,
      "created_at": "2026-05-30T12:00:00+00:00",
      "sender": {
        "id": 1,
        "name": "Sarah Mitchell",
        "email": "s.mitchell@skywest-air.com",
        "role": "admin"
      },
      "recipient": {
        "id": 3,
        "name": "First Officer Ava Chen",
        "email": "a.chen@skywest-air.com",
        "role": "pilot"
      }
    }
  ]
}
```

| Error | Code | When |
|---|---|---|
| Missing token | 401 | No bearer token |
| Forbidden | 403 | Role cannot send, pilot selected recipients, or admin selected non-pilot recipients |
| Bad request | 400 | Empty body, admin omitted `recipient_ids`, or no admins exist |
| Not found | 404 | One or more selected recipients do not exist in the sender's org |

### `GET /api/v1/messages`

List messages visible to the current user.

Query params:

| Param | Values | Default |
|-------|--------|---------|
| `box` | `inbox`, `sent`, `all` | `inbox` |
| `page` | integer >= 1 | `1` |
| `limit` | 1 to 100 | `20` |

Examples:

```text
GET /api/v1/messages
GET /api/v1/messages?box=inbox&page=1&limit=20
GET /api/v1/messages?box=sent
GET /api/v1/messages?box=all
```

**Response `200`:**

```json
{
  "page": 1,
  "limit": 20,
  "total": 1,
  "items": [
    {
      "id": 1,
      "org_id": 1,
      "sender_id": 3,
      "recipient_id": 1,
      "subject": "Issue report",
      "body": "There is a problem with the checklist PDF.",
      "read_at": null,
      "created_at": "2026-05-30T12:00:00+00:00",
      "sender": {
        "id": 3,
        "name": "First Officer Ava Chen",
        "email": "a.chen@skywest-air.com",
        "role": "pilot"
      },
      "recipient": {
        "id": 1,
        "name": "Sarah Mitchell",
        "email": "s.mitchell@skywest-air.com",
        "role": "admin"
      }
    }
  ]
}
```

### `POST /api/v1/messages/{message_id}/read`

Mark a received message as read.

Only the recipient can mark a message as read.

**Response `200`:**

```json
{
  "message": "Message marked as read",
  "item": {
    "id": 1,
    "read_at": "2026-05-30T12:10:00+00:00"
  }
}
```

---

## Running Tests

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest tests/ -v
```

Current tests cover auth, health, and manuals. Message tests should be added next.

---

## Architecture Docs

| Document | Contents |
|----------|----------|
| [`docs/auth_architecture.md`](docs/auth_architecture.md) | Auth flow diagrams, token lifecycle, session management, cryptographic choices |
| [`docs/manual_architecture.md`](docs/manual_architecture.md) | Manual library flows, transaction rollback, storage abstraction, watermarking engine, magic bytes validation, audit logging |
| [`docs/forms_submissions_architecture.md`](docs/forms_submissions_architecture.md) | Forms & submissions flows, RBAC, data dictionary |

Recommended new doc to add later:

| Document | Contents |
|----------|----------|
| `docs/messages_architecture.md` | Pilot/admin messaging flow, RBAC rules, data dictionary, and frontend integration notes |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `skydeck` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `skydeck` | PostgreSQL password |
| `POSTGRES_DB` | `skydeck` | Database name |
| `POSTGRES_SERVER` | `localhost` | Database hostname |
| `POSTGRES_PORT` | `5432` | Database port |
| `DATABASE_URL` | assembled from `POSTGRES_*` | Full connection string override |
| `APP_NAME` | `SkyDeck` | Application name returned by health check |
| `DEBUG` | `false` | Development/debug mode flag |
| `SECRET_KEY` | change me | JWT signing key |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins |
| `STORAGE_DIR` | `storage/manuals` | Manual PDF storage directory |
| `SUBMISSIONS_STORAGE_DIR` | `storage/submissions` | Submission attachment storage |
| `MAX_UPLOAD_SIZE_MB` | `50` | Maximum upload file size |
| `WATERMARK_FONT_SIZE` | `40` | Watermark text size in points |
| `BACKEND_PORT` | `8000` | Uvicorn listen port |
| `RUN_SEED` | `false` | Auto-seed on container start |
| `DB_POOL_SIZE` | `10` | SQLAlchemy pool size |
| `DB_MAX_OVERFLOW` | `20` | Extra DB connections allowed beyond pool size |
| `DB_POOL_RECYCLE` | `300` | Connection recycle time in seconds |

---

## Development Workflow

Option A was chosen for the current repository state:

- Existing direct commits on `main` remain as-is.
- Future repository changes should use an MR-style review flow before being applied.

Preferred workflow going forward:

1. Describe the proposed change.
2. Show changed files and before/after summary.
3. Show a patch-style diff or MR-style summary.
4. Apply only after approval.
5. Include a test plan for backend/frontend behavior.

For backend feature work, use this pattern:

```text
1. Add/change SQLAlchemy model in app/models/
2. Add Alembic migration in alembic/versions/
3. Add Pydantic schemas in app/schemas/
4. Add repository helpers in app/repositories/
5. Add service logic in app/services/ when business logic grows
6. Add FastAPI router in app/api/v1/
7. Register router in app/main.py
8. Add tests
9. Update README/docs
```
