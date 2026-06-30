"""Manual-library HTTP workflows from upload through watermarked download.

This module coordinates the backend's most cross-cutting feature:

* role and tenant authorization;
* PDF validation and filename normalization;
* physical storage plus SQL metadata;
* category and title business rules;
* update-feed and audit records;
* forensic watermarking and accumulated read state.

Storage and PostgreSQL cannot share one atomic transaction, so mutation routes
carefully order operations and clean up where possible when one side fails.
"""

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
    AppError,
    ConflictError,
    NotFoundError,
    PayloadTooLargeError,
    StorageError,
    UnsupportedMediaError,
)
from app.db.session import get_db
from app.models.enums import ManualAction, UserRole
from app.models.manual import Manual
from app.models.manual_category import ManualCategory
from app.models.user import User
from app.repositories import (
    manual_category_repo,
    manual_reads_repo,
    manual_repo,
    manual_update_event_repo,
)
from app.schemas.auth import ErrorResponse
from app.schemas.manual import ManualDeleteOut, ManualOut, ManualUpdateOut, ManualUploadOut
from app.schemas.manual_category import ManualCategoryPathItem
from app.services import audit_service
from app.services.storage import get_manual_storage, secure_filename
from app.services.watermark_service import watermark_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/manuals", tags=["manuals"])

# The magic-byte check catches obvious disguised uploads. Full readability is
# checked later by pypdf when a PDF is watermarked for download.
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
    """Read one upload and return exact bytes, checksum, and safe filename.

    Reading once ensures the checksum and stored object describe identical
    bytes and avoids relying on the mutable stream position later.
    """
    contents = file.file.read()

    if len(contents) > _MAX_BYTES:
        raise PayloadTooLargeError(f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit")

    if len(contents) == 0:
        raise UnsupportedMediaError("Uploaded file is empty")

    if not contents[:5].startswith(_PDF_MAGIC):
        raise UnsupportedMediaError("File is not a valid PDF (magic bytes check failed)")

    # The digest is used for audit/update metadata and content identification.
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
    """Enforce case/whitespace-insensitive active-title uniqueness per tenant.

    During updates ``current_manual_id`` permits a manual to keep its own title
    while still rejecting a collision with another active row.
    """
    existing = manual_repo.get_active_by_title(db, org_id=org_id, title=title)
    if existing and existing.id != current_manual_id:
        raise ConflictError("An active manual with this title already exists")


def _get_category_for_org(
    db: DbSession,
    *,
    org_id: int,
    category_id: int,
) -> ManualCategory:
    """Fetch a category and enforce organization ownership."""
    category = manual_category_repo.get_for_org(db, org_id=org_id, category_id=category_id)
    if category is None:
        raise NotFoundError("Manual category not found")
    return category


def _get_leaf_category_for_org(
    db: DbSession,
    *,
    org_id: int,
    category_id: int,
) -> ManualCategory:
    """Fetch a tenant category and reject non-leaf navigation nodes.

    Keeping manuals only at leaves makes breadcrumb and subtree filtering
    predictable for clients.
    """
    category = _get_category_for_org(db, org_id=org_id, category_id=category_id)
    if manual_category_repo.has_children(db, category_id=category.id):
        raise AppError("Manuals must be assigned to a final leaf category", code=400)
    return category


def _category_path_items(category: ManualCategory) -> list[ManualCategoryPathItem]:
    """Return breadcrumb schema items for a manual's category."""
    
    return [
        ManualCategoryPathItem(id=item.id, name=item.name, slug=item.slug)
        for item in manual_category_repo.get_path(category)
    ]


def _category_path_text(category: ManualCategory) -> str:
    """Return a human-readable category path for audit metadata."""
    
    return " / ".join(item.name for item in manual_category_repo.get_path(category))


def _manual_out(manual: Manual) -> ManualOut:
    """Map an ORM manual into the list/detail response schema."""
    return ManualOut(
        id=manual.id,
        org_id=manual.org_id,
        category_id=manual.category_id,
        category_path=_category_path_items(manual.category),
        category_path_text=_category_path_text(manual.category),
        title=manual.title,
        original_filename=manual.original_filename,
        mime_type=manual.mime_type,
        file_size=manual.file_size,
        version_number=manual.version_number,
        is_active=manual.is_active,
        uploaded_by=manual.uploaded_by,
        created_at=manual.created_at,
        updated_at=manual.updated_at,
    )


def _manual_upload_out(manual: Manual) -> ManualUploadOut:
    """Map an uploaded manual into the upload response schema."""
    return ManualUploadOut(
        id=manual.id,
        category_id=manual.category_id,
        category_path=_category_path_items(manual.category),
        category_path_text=_category_path_text(manual.category),
        title=manual.title,
        original_filename=manual.original_filename,
        file_size=manual.file_size,
        sha256=manual.sha256,
        version_number=manual.version_number,
    )


def _manual_update_out(manual: Manual) -> ManualUpdateOut:
    """Map an updated manual into the update response schema."""
    return ManualUpdateOut(
        id=manual.id,
        category_id=manual.category_id,
        category_path=_category_path_items(manual.category),
        category_path_text=_category_path_text(manual.category),
        title=manual.title,
        original_filename=manual.original_filename,
        file_size=manual.file_size,
        sha256=manual.sha256,
        version_number=manual.version_number,
    )


def _delete_physical_file_or_fail(storage_path: str) -> bool:
    """Delete a stored PDF, verify deletion, and report whether it existed.

    ``StorageProvider.delete`` is intentionally best-effort, so this helper adds
    the stronger verification required by manual deletion semantics.
    """
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
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
    },
    summary="Upload a PDF manual (admin only)",
)
def upload_manual(
    title: str = Form(..., description="Human-readable document title"),
    category_id: int = Form(..., description="Final leaf category selected from the category path"),
    note: Optional[str] = Form(None, description="Manager note shown in the update feed"),
    file: UploadFile = File(..., description="PDF file to upload"),
    request: Request = None,
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    """Create one new manual across storage, metadata, feed, and audit systems.

    Workflow order:
    1. validate title/category/file before creating state;
    2. flush a ``pending`` row to obtain its ID;
    3. use that ID in a collision-resistant storage key;
    4. add feed/audit rows and commit one SQL transaction.
    """
    title = title.strip()
    if not title:
        raise AppError("Manual title is required", code=400)

    category = _get_leaf_category_for_org(
        db,
        org_id=current_user.org_id,
        category_id=category_id,
    )
    _ensure_unique_active_title(db, org_id=current_user.org_id, title=title)
    contents, sha256, safe_name = _read_and_validate_pdf(file)

    storage = get_manual_storage()
    client_ip = request.client.host if request and request.client else None

    # The sentinel reveals interrupted uploads to cleanup tooling and avoids
    # inventing a storage path before the database has allocated an ID.
    manual = manual_repo.create(
        db,
        org_id=current_user.org_id,
        category_id=category.id,
        title=title,
        storage_path="pending",
        original_filename=safe_name,
        mime_type="application/pdf",
        file_size=len(contents),
        sha256=sha256,
        uploaded_by=current_user.id,
    )

    # Create the row first so the storage key can include the database id.
    relative_path = f"{manual.id}_v{manual.version_number}_{safe_name}"
    try:
        disk_path = storage.save(relative_path, contents)
    except StorageError:
        # The SQL row is still uncommitted and can be discarded cleanly.
        db.rollback()
        raise

    manual.storage_path = disk_path

    path_text = _category_path_text(category)
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
        metadata={
            "sha256": sha256,
            "file_size": len(contents),
            "title": title,
            "category_id": category.id,
            "category_path": path_text,
            "note": note,
        },
    )

    # Commit manual metadata, update event, and audit row together.
    db.commit()
    manual = manual_repo.get_by_id(db, manual.id)
    return _manual_upload_out(manual)


# ── POST /{id}/update ─────────────────────────────────────────


@router.post(
    "/{manual_id}/update",
    response_model=ManualUpdateOut,
    responses={
        400: {"model": ErrorResponse},
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
    category_id: Optional[int] = Form(None, description="Optional replacement leaf category"),
    note: Optional[str] = Form(None, description="Manager note shown in the update feed"),
    request: Request = None,
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    """Replace a manual's PDF while retaining version and audit history.

    The new file is saved before the metadata row is changed, so a storage
    failure leaves the old version untouched. Old-file deletion is best-effort
    after the new file is usable; failure may leave an orphan but does not make
    the current manual unavailable.
    """
    manual = manual_repo.get_by_id(db, manual_id)
    if manual is None or manual.org_id != current_user.org_id:
        raise NotFoundError("Manual not found")

    new_title = title.strip() if title is not None else manual.title
    if not new_title:
        raise AppError("Manual title is required", code=400)
    _ensure_unique_active_title(
        db,
        org_id=current_user.org_id,
        title=new_title,
        current_manual_id=manual.id,
    )

    new_category = manual.category
    if category_id is not None:
        new_category = _get_leaf_category_for_org(
            db,
            org_id=current_user.org_id,
            category_id=category_id,
        )

    contents, sha256, safe_name = _read_and_validate_pdf(file)
    storage = get_manual_storage()
    client_ip = request.client.host if request and request.client else None

    # Snapshot old values before mutation so the feed/audit event can describe
    # the transition rather than only the resulting state.
    old_storage_path = manual.storage_path
    old_sha256 = manual.sha256
    old_version_number = manual.version_number
    old_category_id = manual.category_id
    old_category_path = _category_path_text(manual.category)
    next_version = (manual.version_number or 1) + 1
    relative_path = f"{manual.id}_v{next_version}_{safe_name}"

    try:
        # Save the new file before mutating the database row, so rollback is simple on failure.
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
        category_id=new_category.id,
    )
    read_reset_count = manual_reads_repo.mark_manual_unread(
        db,
        org_id=current_user.org_id,
        manual_id=manual.id,
    )

    old_file_deleted = False
    try:
        # Cleanup failure is logged but does not fail the update; the new manual is already usable.
        old_file_deleted = _delete_physical_file_or_fail(old_storage_path)
    except StorageError:
        logger.exception("Manual updated, but old PDF cleanup failed: manual_id=%s", manual.id)

    new_category_path = _category_path_text(new_category)
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
            "old_category_id": old_category_id,
            "new_category_id": new_category.id,
            "old_category_path": old_category_path,
            "new_category_path": new_category_path,
            "old_file_deleted": old_file_deleted,
            "read_reset_count": read_reset_count,
        },
    )

    # Database state now points at the already-saved new object.
    db.commit()
    manual = manual_repo.get_by_id(db, manual.id)
    return _manual_update_out(manual)


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
    """Remove physical bytes, then soft-delete metadata and append history.

    Storage deletion is performed first and verified. If it fails, database
    state remains active so clients are not told a manual was deleted while its
    protected source file still exists.
    """
    manual = manual_repo.get_by_id(db, manual_id)
    if manual is None or manual.org_id != current_user.org_id:
        raise NotFoundError("Manual not found")

    file_deleted = _delete_physical_file_or_fail(manual.storage_path)

    # Capture human/audit details before the model is marked inactive.
    old_storage_path = manual.storage_path
    old_sha256 = manual.sha256
    old_version_number = manual.version_number
    category_id = manual.category_id
    category_path = _category_path_text(manual.category)
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
            "category_id": category_id,
            "category_path": category_path,
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
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="List available manuals, optionally filtered by category path",
)
def list_manuals(
    category_id: Optional[int] = Query(None, description="Category to filter by"),
    include_descendants: bool = Query(True, description="Include manuals in child categories"),
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    """List active tenant manuals, optionally filtered to a category subtree.

    Category ownership is validated separately even when no manuals match,
    preserving a clear 404 for an invalid or cross-tenant filter ID.
    """
    if category_id is not None:
        _get_category_for_org(db, org_id=current_user.org_id, category_id=category_id)

    manuals = manual_repo.list_active(
        db,
        org_id=current_user.org_id,
        category_id=category_id,
        include_descendants=include_descendants,
    )
    return [_manual_out(manual) for manual in manuals]


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
    """Read, watermark, record access/read state, and stream a fresh PDF.

    Watermarking finishes before access state commits, so corrupt/unreadable
    files do not create successful-download evidence. The response includes the
    same forensic hash stored in ``ManualAccessLog``.
    """
    manual = manual_repo.get_by_id(db, manual_id)
    if manual is None or manual.org_id != current_user.org_id:
        raise NotFoundError("Manual not found")

    storage = get_manual_storage()
    if not storage.exists(manual.storage_path):
        raise NotFoundError("Manual file missing from storage")

    # Source bytes stay server-side; the client receives only the watermarked
    # in-memory copy produced below.
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
    manual_reads_repo.mark_read(
        db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        manual_id=manual.id,
    )
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
    # Access log, last-access timestamp, read counter, and generic audit row are
    # one database transaction describing the successful download.
    db.commit()

    download_name = secure_filename(manual.original_filename or f"manual_{manual.id}.pdf")

    # StreamingResponse consumes the rewound BytesIO without another disk write.
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{download_name}"',
            "X-Watermark-Hash": watermark_hash,
        },
    )
