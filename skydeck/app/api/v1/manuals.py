"""Manual Library endpoints with upload/update/delete safety and audit trail."""

from __future__ import annotations

import hashlib
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DbSession

from app.core.config import settings
from app.core.deps import require_roles
from app.core.errors import (
    ConflictError,
    NotFoundError,
    PayloadTooLargeError,
    StorageError,
    UnsupportedMediaError,
)
from app.db.session import get_db
from app.models.enums import ManualAction, UserRole
from app.models.user import User
from app.repositories import manual_repo, manual_update_event_repo
from app.schemas.auth import ErrorResponse
from app.schemas.manual import ManualDeleteOut, ManualOut, ManualUpdateOut, ManualUploadOut
from app.services import audit_service
from app.services.storage import get_manual_storage, secure_filename
from app.services.watermark_service import watermark_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/manuals", tags=["manuals"])

_PDF_MAGIC = b"%PDF-"
_MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

_ADMIN = require_roles(UserRole.admin)
_ALL_ROLES = require_roles(
    UserRole.admin,
    UserRole.pilot,
    UserRole.chief_pilot,
    UserRole.safety,
    UserRole.planning,
    UserRole.technical,
)


def _read_and_validate_pdf(file: UploadFile) -> tuple[bytes, str, str]:
    contents = file.file.read()

    if len(contents) > _MAX_BYTES:
        raise PayloadTooLargeError(f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit")

    if len(contents) == 0:
        raise UnsupportedMediaError("Uploaded file is empty")

    if not contents[:5].startswith(_PDF_MAGIC):
        raise UnsupportedMediaError("File is not a valid PDF (magic bytes check failed)")

    sha256 = hashlib.sha256(contents).hexdigest()
    safe_name = secure_filename(file.filename or "manual.pdf")
    if not safe_name.lower().endswith(".pdf"):
        safe_name += ".pdf"

    return contents, sha256, safe_name


def _ensure_unique_active_title(
    db: DbSession,
    *,
    org_id: int,
    title: str,
    current_manual_id: Optional[int] = None,
) -> None:
    existing = manual_repo.get_active_by_title(db, org_id=org_id, title=title)
    if existing and existing.id != current_manual_id:
        raise ConflictError("An active manual with this title already exists")


def _delete_physical_file_or_fail(storage_path: str) -> bool:
    storage = get_manual_storage()
    if not storage.exists(storage_path):
        return False

    storage.delete(storage_path)
    if storage.exists(storage_path):
        raise StorageError("Failed to delete manual file from storage")
    return True


# ── POST /upload ──────────────────────────────────────────────


@router.post(
    "/upload",
    response_model=ManualUploadOut,
    status_code=201,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
    },
    summary="Upload a PDF manual (admin only)",
)
def upload_manual(
    title: str = Form(..., description="Human-readable document title"),
    note: Optional[str] = Form(None, description="Manager note shown in the update feed"),
    file: UploadFile = File(..., description="PDF file to upload"),
    request: Request = None,
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    title = title.strip()
    if not title:
        raise ConflictError("Manual title is required")

    _ensure_unique_active_title(db, org_id=current_user.org_id, title=title)
    contents, sha256, safe_name = _read_and_validate_pdf(file)

    storage = get_manual_storage()
    client_ip = request.client.host if request and request.client else None

    manual = manual_repo.create(
        db,
        org_id=current_user.org_id,
        title=title,
        storage_path="pending",
        original_filename=safe_name,
        mime_type="application/pdf",
        file_size=len(contents),
        sha256=sha256,
        uploaded_by=current_user.id,
    )

    relative_path = f"{manual.id}_v{manual.version_number}_{safe_name}"
    try:
        disk_path = storage.save(relative_path, contents)
    except StorageError:
        db.rollback()
        raise

    manual.storage_path = disk_path

    manual_update_event_repo.create(
        db,
        org_id=current_user.org_id,
        manual_id=manual.id,
        actor_user_id=current_user.id,
        action="uploaded",
        title=manual.title,
        note=note,
        new_storage_path=disk_path,
        new_sha256=sha256,
        new_version_number=manual.version_number,
    )
    audit_service.record(
        db,
        action="manual.upload",
        target_type="manual",
        target_id=manual.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=client_ip,
        metadata={"sha256": sha256, "file_size": len(contents), "title": title, "note": note},
    )

    db.commit()
    db.refresh(manual)

    return ManualUploadOut(
        id=manual.id,
        title=manual.title,
        original_filename=manual.original_filename,
        file_size=manual.file_size,
        sha256=manual.sha256,
        version_number=manual.version_number,
    )


# ── POST /{id}/update ─────────────────────────────────────────


@router.post(
    "/{manual_id}/update",
    response_model=ManualUpdateOut,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
    },
    summary="Replace the PDF for an existing manual (admin only)",
)
def update_manual(
    manual_id: int,
    file: UploadFile = File(..., description="Replacement PDF file"),
    title: Optional[str] = Form(None, description="Optional replacement title"),
    note: Optional[str] = Form(None, description="Manager note shown in the update feed"),
    request: Request = None,
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    manual = manual_repo.get_by_id(db, manual_id)
    if manual is None or manual.org_id != current_user.org_id:
        raise NotFoundError("Manual not found")

    new_title = title.strip() if title is not None else manual.title
    if not new_title:
        raise ConflictError("Manual title is required")
    _ensure_unique_active_title(
        db,
        org_id=current_user.org_id,
        title=new_title,
        current_manual_id=manual.id,
    )

    contents, sha256, safe_name = _read_and_validate_pdf(file)
    storage = get_manual_storage()
    client_ip = request.client.host if request and request.client else None

    old_storage_path = manual.storage_path
    old_sha256 = manual.sha256
    old_version_number = manual.version_number
    next_version = (manual.version_number or 1) + 1
    relative_path = f"{manual.id}_v{next_version}_{safe_name}"

    try:
        disk_path = storage.save(relative_path, contents)
    except StorageError:
        db.rollback()
        raise

    manual_repo.update_file_metadata(
        db,
        manual,
        storage_path=disk_path,
        original_filename=safe_name,
        file_size=len(contents),
        sha256=sha256,
        uploaded_by=current_user.id,
        title=new_title,
    )

    old_file_deleted = False
    try:
        old_file_deleted = _delete_physical_file_or_fail(old_storage_path)
    except StorageError:
        # Keep the update, but expose the storage cleanup failure in audit metadata.
        logger.exception("Manual updated, but old PDF cleanup failed: manual_id=%s", manual.id)

    manual_update_event_repo.create(
        db,
        org_id=current_user.org_id,
        manual_id=manual.id,
        actor_user_id=current_user.id,
        action="updated",
        title=manual.title,
        note=note,
        old_storage_path=old_storage_path,
        new_storage_path=disk_path,
        old_sha256=old_sha256,
        new_sha256=sha256,
        old_version_number=old_version_number,
        new_version_number=manual.version_number,
    )
    audit_service.record(
        db,
        action="manual.update",
        target_type="manual",
        target_id=manual.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=client_ip,
        metadata={
            "title": manual.title,
            "note": note,
            "old_sha256": old_sha256,
            "new_sha256": sha256,
            "old_version_number": old_version_number,
            "new_version_number": manual.version_number,
            "old_file_deleted": old_file_deleted,
        },
    )

    db.commit()
    db.refresh(manual)

    return ManualUpdateOut(
        id=manual.id,
        title=manual.title,
        original_filename=manual.original_filename,
        file_size=manual.file_size,
        sha256=manual.sha256,
        version_number=manual.version_number,
    )


# ── DELETE /{id} ──────────────────────────────────────────────


@router.delete(
    "/{manual_id}",
    response_model=ManualDeleteOut,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Delete a manual (admin only)",
)
def delete_manual(
    manual_id: int,
    request: Request,
    note: Optional[str] = Query(None, description="Manager note shown in the update feed"),
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    manual = manual_repo.get_by_id(db, manual_id)
    if manual is None or manual.org_id != current_user.org_id:
        raise NotFoundError("Manual not found")

    file_deleted = _delete_physical_file_or_fail(manual.storage_path)

    old_storage_path = manual.storage_path
    old_sha256 = manual.sha256
    old_version_number = manual.version_number
    title = manual.title

    manual_repo.soft_delete(db, manual)
    manual_update_event_repo.create(
        db,
        org_id=current_user.org_id,
        manual_id=manual.id,
        actor_user_id=current_user.id,
        action="deleted",
        title=title,
        note=note,
        old_storage_path=old_storage_path,
        old_sha256=old_sha256,
        old_version_number=old_version_number,
    )
    audit_service.record(
        db,
        action="manual.delete",
        target_type="manual",
        target_id=manual.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=request.client.host if request.client else None,
        metadata={
            "title": title,
            "note": note,
            "old_sha256": old_sha256,
            "old_version_number": old_version_number,
            "physical_file_deleted": file_deleted,
        },
    )
    db.commit()
    return ManualDeleteOut()


# ── GET / (list) ──────────────────────────────────────────────


@router.get(
    "",
    response_model=list[ManualOut],
    responses={401: {"model": ErrorResponse}},
    summary="List available manuals",
)
def list_manuals(
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    return manual_repo.list_active(db, org_id=current_user.org_id)


# ── GET /{id}/download ───────────────────────────────────────


@router.get(
    "/{manual_id}/download",
    responses={
        200: {"content": {"application/pdf": {}}},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Download a watermarked PDF",
)
def download_manual(
    manual_id: int,
    request: Request,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    manual = manual_repo.get_by_id(db, manual_id)
    if manual is None or manual.org_id != current_user.org_id:
        raise NotFoundError("Manual not found")

    storage = get_manual_storage()
    if not storage.exists(manual.storage_path):
        raise NotFoundError("Manual file missing from storage")

    source_bytes = storage.read(manual.storage_path)

    pdf_buffer, watermark_hash = watermark_pdf(
        source_bytes,
        user_name=current_user.name,
        user_id=current_user.id,
        manual_id=manual.id,
    )

    client_ip = request.client.host if request.client else None
    manual_repo.record_access(
        db,
        org_id=manual.org_id,
        manual_id=manual.id,
        user_id=current_user.id,
        action=ManualAction.download,
        watermark_hash_id=watermark_hash,
        ip=client_ip,
    )
    manual_repo.touch_last_accessed(db, manual)
    audit_service.record(
        db,
        action="manual.download",
        target_type="manual",
        target_id=manual.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=client_ip,
        metadata={"watermark_hash": watermark_hash},
    )
    db.commit()

    download_name = secure_filename(manual.original_filename or f"manual_{manual.id}.pdf")

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{download_name}"',
            "X-Watermark-Hash": watermark_hash,
        },
    )
