# SkyDeck API

FastAPI backend for the SkyDeck aviation safety system. The backend provides
authentication, organization-scoped users, manual library management, manual
update notifications, digital forms/submissions, internal messaging, encrypted
message attachments, encrypted user profile pictures, and audit logging.

This README is focused on the backend inside `skydeck/`. The React frontend
lives at the repository root.

## Table of Contents

1. [Backend Overview](#backend-overview)
2. [Repository Layout](#repository-layout)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Database and Migrations](#database-and-migrations)
6. [Seed Data](#seed-data)
7. [Security Model](#security-model)
8. [API Guide](#api-guide)
9. [Frontend Integration Notes](#frontend-integration-notes)
10. [Testing](#testing)
11. [Development Workflow](#development-workflow)

## Backend Overview

### Stack

| Area | Technology |
| --- | --- |
| API | FastAPI |
| Database ORM | SQLAlchemy 2.0 sync ORM |
| Migrations | Alembic |
| Database | PostgreSQL |
| Auth | JWT access tokens + refresh-token sessions |
| Passwords | bcrypt |
| File storage | Local disk through `StorageProvider` abstraction |
| PDF watermarking | `pypdf` + `reportlab` |
| File encryption | AES-256-GCM through `cryptography` |

### Main Capabilities

- JWT signup, login, refresh, and logout.
- Refresh-token session tracking in the `sessions` table.
- Role-based access control with organization scoping.
- User profile fields for crew/profile UI:
  - `employee_no`
  - `position`
  - `aircraft_type`
  - `medical_expires_at`
  - `passport_expires_at`
  - `license_expires_at`
  - `profile_picture_id`
  - `profile_picture_url`
- Encrypted user profile pictures.
- Manual upload, update, list, download, and delete.
- Manual category tree/path support.
- Manual update feed with persisted per-user read state.
- Digital form templates and versioned form schemas.
- Digital form submissions with optional attachments.
- Internal pilot/admin messaging.
- Sender-visible message read receipts.
- Admin recipient lookup for pilot/chief-pilot selection.
- Encrypted message attachments.
- Central audit logging in `audit_logs`.

## Repository Layout

```text
program/
|-- package.json                 # Frontend dependencies/scripts
|-- vite.config.js               # Frontend dev proxy to backend
|-- src/                         # React frontend
`-- skydeck/                     # FastAPI backend
    |-- app/
    |   |-- api/v1/              # Versioned API routers
    |   |-- core/                # Config, security, dependencies, errors
    |   |-- db/                  # SQLAlchemy engine/session/base
    |   |-- models/              # SQLAlchemy ORM models
    |   |-- repositories/        # Data access helpers
    |   |-- schemas/             # Pydantic request/response models
    |   |-- services/            # Business/security/storage helpers
    |   `-- main.py              # FastAPI app assembly
    |-- alembic/versions/        # DB migration files
    |-- docs/                    # Extra architecture notes
    |-- tests/                   # Pytest suite
    |-- requirements.txt
    |-- requirements-dev.txt
    |-- pyproject.toml
    `-- README.md
```

## Quick Start

### 1. Enter the Backend Directory

```powershell
cd E:\work\efb\program\skydeck
```

### 2. Create `.env`

```powershell
Copy-Item .env.example .env
```

For local development, the default database values are usually fine. Do change
secrets before production:

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
FILE_ENCRYPTION_MASTER_KEY=CHANGE-ME-generate-a-separate-64-byte-random-key

CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
RUN_SEED=true
```

Generate production-grade secrets with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Use different values for `SECRET_KEY` and `FILE_ENCRYPTION_MASTER_KEY`.

### 3. Create and Activate a Virtual Environment

From `skydeck/`:

```powershell
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
```

If you prefer the virtualenv inside `skydeck/`, this also works:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

For local test/lint tooling:

```powershell
pip install -r requirements-dev.txt
```

### 5. Start PostgreSQL

With Docker Desktop:

```powershell
docker compose -f deploy-assets/docker-compose.yml up -d db pgadmin
```

Or create a local PostgreSQL database manually:

```sql
CREATE USER skydeck WITH PASSWORD 'skydeck';
CREATE DATABASE skydeck OWNER skydeck;
GRANT ALL PRIVILEGES ON DATABASE skydeck TO skydeck;
```

### 6. Run Migrations

```powershell
python -m alembic upgrade head
```

The current head is:

```text
0008_user_profile_pictures.py
```

### 7. Seed Demo Data

```powershell
python -m app.seed
```

The seed script skips if the database already contains organizations.

### 8. Start the Backend

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Or:

```powershell
.\start_server.ps1
```

Useful URLs:

| Page | URL |
| --- | --- |
| Swagger UI | `http://127.0.0.1:8000/docs` |
| ReDoc | `http://127.0.0.1:8000/redoc` |
| Health check | `http://127.0.0.1:8000/health` |

## Configuration

Settings are loaded from environment variables first, then `skydeck/.env`, then
defaults in `app/core/config.py`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `POSTGRES_USER` | `skydeck` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `skydeck` | PostgreSQL password |
| `POSTGRES_DB` | `skydeck` | PostgreSQL database |
| `POSTGRES_SERVER` | `localhost` | PostgreSQL host |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `DATABASE_URL` | assembled | Full SQLAlchemy URL override |
| `APP_NAME` | `SkyDeck` | App name in health response |
| `DEBUG` | `false` | Debug flag; must be boolean-like |
| `BACKEND_PORT` | `8000` | Uvicorn port used by launcher scripts |
| `SECRET_KEY` | change me | JWT signing key and last-resort crypto fallback |
| `FILE_ENCRYPTION_MASTER_KEY` | `None` | Preferred master key for encrypted files |
| `MESSAGE_ATTACHMENT_MASTER_KEY` | `None` | Legacy fallback key for encrypted attachments |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT access-token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh-token lifetime |
| `CORS_ORIGINS` | localhost Vite/React origins | Allowed browser origins |
| `STORAGE_DIR` | `storage/manuals` | Manual PDF storage |
| `SUBMISSIONS_STORAGE_DIR` | `storage/submissions` | Submission attachment storage |
| `MESSAGE_ATTACHMENTS_STORAGE_DIR` | `storage/message_attachments` | Encrypted message attachment storage |
| `PROFILE_PICTURES_STORAGE_DIR` | `storage/profile_pictures` | Encrypted profile picture storage |
| `MESSAGE_ATTACHMENT_MAX_FILE_MB` | `25` | Max size per message attachment |
| `MESSAGE_ATTACHMENT_MAX_FILES` | `5` | Max attachments per message send |
| `MESSAGE_ATTACHMENT_MAX_TOTAL_MB` | `50` | Max total attachment bytes per message send |
| `PROFILE_PICTURE_MAX_FILE_MB` | `5` | Max profile picture upload size |
| `MAX_UPLOAD_SIZE_MB` | `50` | Manual PDF upload size limit |
| `WATERMARK_FONT_SIZE` | `40` | Manual watermark font size |
| `RUN_SEED` | `false` | Container entrypoint seed toggle |
| `DB_POOL_SIZE` | `10` | SQLAlchemy pool size |
| `DB_MAX_OVERFLOW` | `20` | Extra connections beyond pool |
| `DB_POOL_RECYCLE` | `300` | Connection recycle seconds |

Important security notes:

- Do not deploy with `CHANGE-ME...` secrets.
- Keep `FILE_ENCRYPTION_MASTER_KEY` backed up securely.
- Losing the file encryption key makes encrypted attachments/profile pictures
  unrecoverable.
- Changing the key without migration means old encrypted files cannot decrypt.

## Database and Migrations

### Current Migration Chain

| Revision | Description |
| --- | --- |
| `0001_initial_schema.py` | Auth, orgs, users, manuals, forms, submissions, audit logs |
| `0002_add_messages.py` | Internal messages |
| `0003_manual_update_events_and_manual_uniqueness.py` | Manual update feed and active title uniqueness |
| `0004_manual_category_paths.py` | Manual category hierarchy and manual category backfill |
| `0005_user_profile_fields.py` | Crew/profile fields on users |
| `0006_manual_update_reads.py` | Per-user manual update read state |
| `0007_message_attachments.py` | Encrypted message attachment metadata |
| `0008_user_profile_pictures.py` | Encrypted profile pictures and user reference |

Check the current database revision:

```powershell
python -m alembic current
```

Upgrade:

```powershell
python -m alembic upgrade head
```

### Main Tables

```text
orgs
users
user_profile_pictures
sessions
login_attempts
manual_categories
manuals
manual_access_logs
manual_update_events
manual_update_reads
form_templates
form_versions
submissions
submission_attachments
messages
message_attachments
audit_logs
```

### Viewing Schema

With Docker:

```powershell
docker compose -f deploy-assets/docker-compose.yml exec db psql -U skydeck -d skydeck
```

Useful `psql` commands:

```sql
\dt
\d users
\d user_profile_pictures
\d messages
\d message_attachments
\d manual_update_reads
```

## Seed Data

All seeded users use:

```text
SkyDeck@2026!
```

| Role | Name | Email |
| --- | --- | --- |
| `admin` | Sarah Mitchell | `s.mitchell@skywest-air.com` |
| `chief_pilot` | Captain James Thornton | `j.thornton@skywest-air.com` |
| `pilot` | First Officer Ava Chen | `a.chen@skywest-air.com` |
| `pilot` | First Officer Marcus Rivera | `m.rivera@skywest-air.com` |
| `pilot` | Captain Nadia Okonkwo | `n.okonkwo@skywest-air.com` |

Verify seeded users:

```powershell
python -c "from app.db.session import SessionLocal; from app.models.user import User; db=SessionLocal(); [print(u.id, u.email, u.name, u.role) for u in db.query(User).all()]; db.close()"
```

If local seed state is stale, reset the Docker DB:

```powershell
docker compose -f deploy-assets/docker-compose.yml down -v
docker compose -f deploy-assets/docker-compose.yml up -d db pgadmin
python -m alembic upgrade head
python -m app.seed
```

## Security Model

### Authentication

- Access tokens are JWTs signed with `SECRET_KEY`.
- Refresh tokens are stored only as SHA-256 hashes.
- Every successful login creates a `sessions` row.
- Logout revokes the refresh-token session.
- Protected routes use `get_current_user` and role dependencies.

### Organization Scoping

Most business data includes `org_id`. API routes enforce same-org access before
returning data, downloading files, or accepting recipient ids. This is especially
important for:

- messages
- message attachments
- manual update reads
- user profile pictures
- manuals and categories
- submissions

### Manual PDFs

Manual PDFs are not encrypted at rest in the current implementation. They are
protected by:

- authenticated API access
- role checks for upload/update/delete
- organization scoping
- PDF magic-byte validation
- secure filename handling
- storage path traversal protection
- SHA-256 content hash
- audit logs
- forensic watermarking on download

On download, the server reads the stored PDF, applies a watermark in memory, and
streams the watermarked PDF. The watermark includes:

```text
CONFIDENTIAL
user name
timestamp
watermark hash id
```

### Encrypted Message Attachments and Profile Pictures

Message attachments and profile pictures are encrypted at rest.

Encryption details:

- Algorithm: AES-256-GCM.
- Each file gets a random 256-bit data key.
- Each file gets a random content nonce.
- Plaintext is encrypted in memory.
- The per-file data key is encrypted by a master key.
- The master key is derived from `FILE_ENCRYPTION_MASTER_KEY`.
- Stored file bytes are ciphertext only.
- Metadata is stored in PostgreSQL.

Metadata stored for encrypted files:

```text
storage_path
original_filename
mime_type
file_size
sha256                  # hash of plaintext, used after decrypt
encrypted_key           # encrypted per-file data key
key_nonce               # nonce for encrypted_key
content_nonce           # nonce for file ciphertext
encryption_key_id
encryption_alg
created_at
```

The browser never receives encryption keys and never decrypts files. The backend
does all decryption after authorization.

Download/decryption flow:

1. Frontend calls a protected download endpoint.
2. Backend verifies the current user's JWT.
3. Backend verifies same-org visibility and resource ownership rules.
4. Backend reads ciphertext from storage.
5. Backend reads encryption metadata from the DB.
6. Backend decrypts the per-file data key using the master key.
7. Backend decrypts ciphertext using the data key.
8. Backend verifies SHA-256 of the plaintext.
9. Backend audit-logs the download.
10. Backend streams plaintext to the frontend.

### Is Encryption Reversible?

Yes. Attachments and profile pictures use reversible encryption. That is required
because users need to download/view the original file later.

For backend EDA or operational tooling, decryption requires:

- database metadata row,
- encrypted file from storage,
- the same `FILE_ENCRYPTION_MASTER_KEY` used during upload.

If the master key is lost, the encrypted files cannot be recovered.

### Example EDA Decryption: Message Attachment

Run from `skydeck/` with the correct environment loaded:

```python
from pathlib import Path

from app.db.session import SessionLocal
from app.repositories import message_repo
from app.services.attachment_crypto import decrypt_attachment
from app.services.storage import get_message_attachment_storage

db = SessionLocal()
try:
    attachment = message_repo.get_attachment_for_message(
        db,
        org_id=1,
        message_id=123,
        attachment_id=456,
    )
    storage = get_message_attachment_storage()
    ciphertext = storage.read(attachment.storage_path)

    plaintext = decrypt_attachment(
        ciphertext=ciphertext,
        encrypted_key=attachment.encrypted_key,
        key_nonce=attachment.key_nonce,
        content_nonce=attachment.content_nonce,
    )

    Path(attachment.original_filename or "decrypted_attachment").write_bytes(plaintext)
finally:
    db.close()
```

### Example EDA Decryption: Profile Picture

```python
from pathlib import Path

from app.db.session import SessionLocal
from app.repositories import user_repo
from app.services.attachment_crypto import decrypt_profile_picture
from app.services.storage import get_profile_picture_storage

db = SessionLocal()
try:
    picture = user_repo.get_profile_picture(db, org_id=1, picture_id=10)
    storage = get_profile_picture_storage()
    ciphertext = storage.read(picture.storage_path)

    plaintext = decrypt_profile_picture(
        ciphertext=ciphertext,
        encrypted_key=picture.encrypted_key,
        key_nonce=picture.key_nonce,
        content_nonce=picture.content_nonce,
    )

    Path(picture.original_filename or "profile_picture").write_bytes(plaintext)
finally:
    db.close()
```

## API Guide

All API paths below are prefixed with:

```text
/api/v1
```

### Auth

#### `POST /auth/signup`

Admin-only endpoint for creating a user in the current admin's organization.
If `role` is omitted, the new user defaults to `pilot`.

Supported roles:

```text
pilot
chief_pilot
admin
safety
planning
technical
```

Use `pilot` for copilot/first-officer style users. Use `chief_pilot` for the
chief pilot role.

Request:

```json
{
  "name": "Ali",
  "email": "ali@example.com",
  "password": "123456",
  "role": "pilot"
}
```

Response:

```json
{
  "user_id": 12,
  "role": "pilot",
  "access_token": "...",
  "refresh_token": "..."
}
```

#### `POST /auth/login`

Request:

```json
{
  "email": "s.mitchell@skywest-air.com",
  "password": "SkyDeck@2026!",
  "device_info": {
    "platform": "Web"
  }
}
```

Response:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Sarah Mitchell",
    "role": "admin"
  }
}
```

#### `POST /auth/refresh`

```json
{
  "refresh_token": "..."
}
```

#### `POST /auth/logout`

```json
{
  "refresh_token": "..."
}
```

### Users and Profile Pictures

#### `GET /users`

Admin-only endpoint that lists active users in the current admin's organization.
Soft-deleted users are not returned.

Response shape:

```json
[
  {
    "id": 3,
    "org_id": 1,
    "name": "First Officer Ava Chen",
    "email": "a.chen@skywest-air.com",
    "role": "pilot",
    "employee_no": "3",
    "position": "P2",
    "aircraft_type": "A310",
    "license_expires_at": "2027-06-07T00:00:00+00:00",
    "profile_picture_id": 10,
    "profile_picture_url": "/api/v1/users/3/profile-picture",
    "created_at": "2026-06-07T00:00:00+00:00",
    "updated_at": null
  }
]
```

#### `DELETE /users/{user_id}`

Admin-only endpoint that soft-deletes a user in the current admin's organization.
The user row is preserved for audit/history references, but the user can no
longer log in and no longer appears in `GET /users`.

Admins cannot delete their own account.

Response:

```json
{
  "message": "User deleted successfully"
}
```

#### `GET /users/me`

Returns the current authenticated user.

Response shape:

```json
{
  "id": 3,
  "org_id": 1,
  "name": "First Officer Ava Chen",
  "email": "a.chen@skywest-air.com",
  "role": "pilot",
  "employee_no": "3",
  "position": "P2",
  "aircraft_type": "A310",
  "medical_expires_at": "2027-06-07T00:00:00+00:00",
  "passport_expires_at": "2031-06-07T00:00:00+00:00",
  "license_expires_at": "2027-06-07T00:00:00+00:00",
  "profile_picture_id": 10,
  "profile_picture_url": "/api/v1/users/3/profile-picture",
  "created_at": "2026-06-07T00:00:00+00:00",
  "updated_at": null
}
```

#### `POST /users/me/profile-picture`

Uploads and encrypts the current user's profile picture.

Request: `multipart/form-data`

| Field | Type | Required |
| --- | --- | --- |
| `file` | JPG, PNG, GIF, or WebP | Yes |

Validation:

- max size comes from `PROFILE_PICTURE_MAX_FILE_MB`,
- content is checked by magic bytes,
- filename is sanitized,
- file is encrypted before storage.

Response: updated `UserMeResponse`.

#### `GET /users/me/profile-picture`

Downloads the current user's profile picture.

The backend decrypts in memory and streams image bytes. The frontend can use this
as an authenticated image download. If using an `<img>`, the frontend may need to
fetch the blob with auth headers and convert it to an object URL.

#### `GET /users/{user_id}/profile-picture`

Downloads another user's profile picture if the target user is in the same org.

### Manuals

#### `POST /manuals/upload`

Admin-only PDF upload.

Request: `multipart/form-data`

| Field | Type | Required |
| --- | --- | --- |
| `title` | string | Yes |
| `category_id` | int | Yes |
| `note` | string | No |
| `file` | PDF | Yes |

Validation pipeline:

```text
size limit -> PDF magic bytes -> SHA-256 -> secure filename -> storage -> audit
```

#### `POST /manuals/{manual_id}/update`

Admin-only PDF replacement. Can also change `title`, `category_id`, and `note`.
Creates a manual update feed entry.

#### `GET /manuals`

Lists active manuals for the current user's org. Supports optional category
filtering:

```text
GET /api/v1/manuals?category_id=12&include_descendants=true
```

#### `GET /manuals/{manual_id}/download`

Downloads a watermarked PDF. Response includes `X-Watermark-Hash`.

#### `DELETE /manuals/{manual_id}`

Admin-only soft delete plus physical file delete.

### Manual Categories

The manual category API supports a tree-shaped frontend selector.

```text
GET /manual-categories/roots
GET /manual-categories/{category_id}/children
GET /manual-categories/{category_id}/path
GET /manual-categories/tree
```

Manual uploads must use a leaf category.

### Manual Updates

Manual updates are user-visible feed entries created when manuals are uploaded,
updated, or deleted.

#### `GET /manual-updates`

Returns paginated update feed entries with per-user read state:

```json
{
  "page": 1,
  "limit": 20,
  "total": 1,
  "items": [
    {
      "id": 44,
      "org_id": 1,
      "manual_id": 5,
      "actor_user_id": 1,
      "action": "updated",
      "title": "A310 SOP",
      "note": "Revision 2 uploaded",
      "is_read": false,
      "read_at": null,
      "created_at": "2026-06-07T00:00:00+00:00"
    }
  ]
}
```

#### `POST /manual-updates/{event_id}/read`

Marks one update read for the current user.

#### `POST /manual-updates/read-all`

Marks all currently existing updates read for the current user. Future update
events still appear unread.

### Forms and Submissions

#### `GET /forms/active`

Returns latest active form versions for the current org.

#### `POST /submissions`

Creates a form submission. Request is `multipart/form-data`.

| Field | Type | Required |
| --- | --- | --- |
| `form_version_id` | int | Yes |
| `data` | JSON string | Yes |
| `file` | file | No |

#### `GET /submissions`

Admin/viewer listing.

#### `GET /submissions/{submission_id}`

Admin/viewer detail response including attachment metadata.

### Messages

Messaging is direct user-to-user storage, but sending rules are role based.

| Sender role | Recipient rule |
| --- | --- |
| `pilot` | Sends to all admins in same org |
| `chief_pilot` | Sends to all admins in same org |
| `admin` | Sends to selected `pilot` or `chief_pilot` ids |
| `safety`, `planning`, `technical` | Not allowed to send messages yet |

#### `GET /messages/recipients`

Admin-only endpoint for the frontend recipient picker. Returns active same-org
pilots/chief pilots.

Response:

```json
[
  {
    "id": 3,
    "name": "First Officer Ava Chen",
    "email": "a.chen@skywest-air.com",
    "role": "pilot",
    "employee_no": "3",
    "position": "P2",
    "aircraft_type": "A310"
  }
]
```

#### `POST /messages`

JSON-only message send.

Pilot/chief pilot request:

```json
{
  "subject": "Issue report",
  "body": "There is a problem with the checklist PDF."
}
```

Admin request:

```json
{
  "subject": "Response",
  "body": "Thanks, I checked it.",
  "recipient_ids": [3, 4]
}
```

#### `POST /messages/with-attachments`

Multipart message send with encrypted attachments.

Fields:

| Field | Type | Required |
| --- | --- | --- |
| `subject` | string | No |
| `body` | string | Yes |
| `recipient_ids` | JSON array string or comma-separated ids | Admin only |
| `files` | one or more files | No |

Allowed attachments:

- JPG/JPEG
- PNG
- GIF
- WebP
- PDF
- UTF-8 text-like files: `.txt`, `.csv`, `.log`
- OpenXML Office files: `.docx`, `.xlsx`, `.pptx`

Rejected:

- empty files,
- files over configured size limits,
- files whose content does not match extension,
- executable/binary types not in the allowlist,
- archives except valid OpenXML Office documents.

#### `GET /messages`

Lists messages visible to the current user.

Query params:

| Param | Values | Default |
| --- | --- | --- |
| `box` | `inbox`, `sent`, `all` | `inbox` |
| `page` | integer >= 1 | `1` |
| `limit` | 1 to 100 | `20` |

Response items include read receipt fields and attachment metadata:

```json
{
  "id": 1,
  "org_id": 1,
  "sender_id": 3,
  "recipient_id": 1,
  "subject": "Issue report",
  "body": "There is a problem with the checklist PDF.",
  "is_read": true,
  "read_by_recipient": true,
  "read_at": "2026-06-07T12:10:00+00:00",
  "created_at": "2026-06-07T12:00:00+00:00",
  "attachments": [
    {
      "id": 9,
      "original_filename": "photo.png",
      "mime_type": "image/png",
      "file_size": 2048,
      "created_at": "2026-06-07T12:00:00+00:00"
    }
  ]
}
```

#### `POST /messages/{message_id}/read`

Recipient-only. Sets `read_at`. Senders then see `read_by_recipient: true` in
`sent` or `all` message listings.

#### `GET /messages/{message_id}/attachments/{attachment_id}`

Downloads one encrypted attachment after authorization. Only the message sender
or recipient can download it.

The backend decrypts and streams plaintext. The frontend does not see keys.

## Frontend Integration Notes

### Auth

Store:

- `access_token`
- `refresh_token`
- returned `user` object

Send protected requests with:

```http
Authorization: Bearer <access_token>
```

### Profile Pictures

Recommended frontend flow:

1. Call `GET /users/me`.
2. If `profile_picture_url` is present, fetch it with auth headers.
3. Convert response blob to an object URL for display.
4. Upload new images with `POST /users/me/profile-picture`.
5. Refresh `/users/me` after upload.

### Message Recipient Picker

Admin UI should call:

```text
GET /api/v1/messages/recipients
```

The frontend should display names, but submit selected ids through
`recipient_ids`.

### Read Receipts

For inbox unread style:

- unread if `read_at === null`.

For sent-message receipt style:

- show "seen" if `read_by_recipient === true`,
- optionally show the timestamp from `read_at`.

### Manual Update Notifications

The backend now owns read state. Avoid localStorage-only read tracking for
production behavior.

Recommended flow:

1. Poll or refresh `GET /manual-updates`.
2. Badge count is `items.filter(item => !item.is_read).length`.
3. When user opens one item, call `POST /manual-updates/{id}/read`.
4. For "mark all", call `POST /manual-updates/read-all`.

## Testing

Run all tests:

```powershell
python -m pytest
```

Run smoke tests:

```powershell
python -m pytest tests/test_auth.py tests/test_health.py
```

Run lint checks:

```powershell
python -m ruff check app tests
```

Current caveat: some manual tests may depend on a fully seeded database and older
manual upload assumptions. If manual upload tests return `422`, check that the
test supplies the required `category_id`.

## Development Workflow

For backend feature work:

1. Add or update SQLAlchemy models in `app/models/`.
2. Register new models in `app/models/__init__.py`.
3. Add an Alembic migration in `alembic/versions/`.
4. Add Pydantic schemas in `app/schemas/`.
5. Add repository helpers in `app/repositories/`.
6. Add service helpers in `app/services/` for business logic, validation, crypto, or storage.
7. Add/extend FastAPI routes in `app/api/v1/`.
8. Register new routers in `app/main.py` if needed.
9. Run targeted checks.
10. Run smoke or full tests.
11. Update README/docs.

Suggested checks for small backend changes:

```powershell
python -m ruff check <changed files>
python -m compileall <changed files>
python -m pytest tests/test_auth.py tests/test_health.py
```

Migration checklist:

- migration upgrades cleanly from current head,
- downgrade is present,
- nullable/backfill strategy is safe for existing data,
- ORM model and migration agree,
- app imports successfully after migration.

## Operational Notes

- Back up PostgreSQL and encrypted file storage together.
- Back up `FILE_ENCRYPTION_MASTER_KEY` in the same disaster-recovery plan.
- Treat encrypted storage without DB metadata as unusable.
- Treat DB metadata without encrypted storage bytes as unusable.
- Do not log plaintext file contents.
- Do not expose `encrypted_key`, nonces, storage paths, or SHA values in public API responses.
- Prefer backend download endpoints over direct file serving so auth, decryption,
  integrity verification, and audit logs always run.
