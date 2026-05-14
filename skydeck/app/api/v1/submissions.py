"""Form submissions endpoints.

Pilots submit forms; admins and viewers can list/view them.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session as DbSession

from app.core.config import settings
from app.core.deps import require_roles
from app.core.errors import AppError, NotFoundError, PayloadTooLargeError
from app.db.session import get_db
from app.models.enums import SubmissionStatus, UserRole
from app.models.submission import Submission
from app.models.submission_attachment import SubmissionAttachment
from app.models.user import User
from app.repositories import form_repo, submission_repo
from app.schemas.auth import ErrorResponse
from app.schemas.pagination import PaginatedResponse
from app.schemas.submission import (
    SubmissionCreateOut,
    SubmissionDetailOut,
    SubmissionOut,
)
from app.services import audit_service
from app.services.storage import get_submission_storage, secure_filename

router = APIRouter(prefix="/submissions", tags=["submissions"])

_PILOT_ROLES = require_roles(UserRole.pilot, UserRole.chief_pilot, UserRole.admin)
_VIEWER_ROLES = require_roles(
    UserRole.admin,
    UserRole.safety,
    UserRole.planning,
    UserRole.technical,
    UserRole.chief_pilot,
)


def _generate_hash_id() -> str:
    raw = f"{secrets.token_hex(16)}:{datetime.now(timezone.utc).isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


# ── POST / (submit form) ────────────────────────────────────


@router.post(
    "",
    response_model=SubmissionCreateOut,
    status_code=201,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Submit a form (pilot/admin)",
)
def create_submission(
    request: Request,
    form_version_id: int = Form(...),
    data: str = Form(..., description="JSON string of form field responses"),
    file: Optional[UploadFile] = File(None, description="Optional attachment"),
    current_user: User = Depends(_PILOT_ROLES),
    db: DbSession = Depends(get_db),
):
    import json as _json

    version = form_repo.get_version_by_id(db, form_version_id)
    if version is None:
        raise NotFoundError("Form version not found")

    if version.template.org_id != current_user.org_id:
        raise NotFoundError("Form version not found")

    try:
        data_dict = _json.loads(data)
    except _json.JSONDecodeError as exc:
        raise AppError("Invalid JSON in data field", code=400) from exc

    if not isinstance(data_dict, dict):
        raise AppError("Form data must be a JSON object", code=400)

    now = datetime.now(timezone.utc)
    hash_id = _generate_hash_id()
    client_ip = request.client.host if request.client else None

    sub = Submission(
        org_id=current_user.org_id,
        user_id=current_user.id,
        form_version_id=form_version_id,
        data_json=data_dict,
        status=SubmissionStatus.submitted,
        hash_id=hash_id,
        ip=client_ip,
        submitted_at=now,
    )
    submission_repo.create(db, submission=sub)

    _max_attach = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file is not None and file.filename:
        contents = file.file.read()
        if len(contents) > _max_attach:
            raise PayloadTooLargeError(f"Attachment exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit")
        if len(contents) > 0:
            storage = get_submission_storage()
            safe_name = secure_filename(file.filename)
            rel_path = f"{sub.id}_{safe_name}"
            disk_path = storage.save(rel_path, contents)

            attachment = SubmissionAttachment(
                submission_id=sub.id,
                storage_path=disk_path,
                original_filename=safe_name,
                mime_type=file.content_type,
                file_size=len(contents),
                sha256=hashlib.sha256(contents).hexdigest(),
                attachment_type="submission_attachment",
            )
            db.add(attachment)
            db.flush()

    audit_service.record(
        db,
        action="submission.create",
        target_type="submission",
        target_id=sub.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=client_ip,
        metadata={"form_version_id": form_version_id, "hash_id": hash_id},
    )
    db.commit()

    return SubmissionCreateOut(
        submission_id=sub.id,
        hash_id=sub.hash_id,
        status=sub.status.value,
    )


# ── GET / (list, paginated) ──────────────────────────────────


@router.get(
    "",
    response_model=PaginatedResponse[SubmissionOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
    summary="List all submissions (admin/viewer)",
)
def list_submissions(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(_VIEWER_ROLES),
    db: DbSession = Depends(get_db),
):
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    offset = (page - 1) * limit
    items, total = submission_repo.list_by_org(
        db, org_id=current_user.org_id, offset=offset, limit=limit
    )

    return PaginatedResponse(
        page=page,
        limit=limit,
        total=total,
        items=[SubmissionOut.model_validate(s) for s in items],
    )


# ── GET /{id} (single) ───────────────────────────────────────


@router.get(
    "/{submission_id}",
    response_model=SubmissionDetailOut,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="View a single submission",
)
def get_submission(
    submission_id: int,
    request: Request,
    current_user: User = Depends(_VIEWER_ROLES),
    db: DbSession = Depends(get_db),
):
    sub = submission_repo.get_by_id(db, submission_id)
    if sub is None or sub.org_id != current_user.org_id:
        raise NotFoundError("Submission not found")

    audit_service.record(
        db,
        action="submission.view",
        target_type="submission",
        target_id=sub.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=request.client.host if request.client else None,
    )
    db.commit()

    return SubmissionDetailOut.model_validate(sub)
