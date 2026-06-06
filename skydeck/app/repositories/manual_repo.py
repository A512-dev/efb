"""Repository helpers for manuals and manual access logging.

Repository modules keep SQLAlchemy query details out of API handlers and
services. They generally flush pending changes but leave transaction commit or
rollback decisions to their callers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession, joinedload

from app.models.enums import ManualAction
from app.models.manual import Manual
from app.models.manual_access_log import ManualAccessLog
from app.models.manual_category import ManualCategory

# ── manuals CRUD ──────────────────────────────────────────────


def create(
    db: DbSession,
    *,
    org_id: int,
    category_id: int,
    title: str,
    storage_path: str,
    original_filename: Optional[str] = None,
    mime_type: Optional[str] = None,
    file_size: Optional[int] = None,
    sha256: Optional[str] = None,
    uploaded_by: Optional[int] = None,
) -> Manual:
    """Create the database row for a manual upload.

    File bytes are handled by the storage service. This row stores the metadata
    needed to locate, version, and audit the uploaded manual.
    """
    manual = Manual(
        org_id=org_id,
        category_id=category_id,
        title=title,
        storage_path=storage_path,
        original_filename=original_filename,
        mime_type=mime_type,
        file_size=file_size,
        sha256=sha256,
        uploaded_by=uploaded_by,
    )
    db.add(manual)
    db.flush()
    return manual


def _category_descendant_ids(db: DbSession, *, org_id: int, category_id: int):
    """Build a recursive query for a category and its active descendants."""
    descendants = (
        select(ManualCategory.id)
        .where(ManualCategory.id == category_id, ManualCategory.org_id == org_id)
        .cte(name="manual_category_descendants", recursive=True)
    )
    descendants = descendants.union_all(
        select(ManualCategory.id).where(
            ManualCategory.parent_id == descendants.c.id,
            ManualCategory.org_id == org_id,
            ManualCategory.is_active.is_(True),
        )
    )
    return select(descendants.c.id)


def list_active(
    db: DbSession,
    *,
    org_id: int,
    category_id: Optional[int] = None,
    include_descendants: bool = True,
) -> list[Manual]:
    """List active manuals, optionally scoped to a category subtree."""
    query = (
        db.query(Manual)
        .options(joinedload(Manual.category))
        .filter(Manual.org_id == org_id, Manual.deleted_at.is_(None), Manual.is_active.is_(True))
    )

    if category_id is not None:
        if include_descendants:
            query = query.filter(
                Manual.category_id.in_(
                    _category_descendant_ids(db, org_id=org_id, category_id=category_id)
                )
            )
        else:
            query = query.filter(Manual.category_id == category_id)

    return query.order_by(Manual.created_at.desc()).all()


def get_by_id(db: DbSession, manual_id: int) -> Optional[Manual]:
    """Fetch a non-deleted manual by primary key, including its category."""
    return (
        db.query(Manual)
        .options(joinedload(Manual.category))
        .filter(Manual.id == manual_id, Manual.deleted_at.is_(None))
        .first()
    )


def get_active_by_title(db: DbSession, *, org_id: int, title: str) -> Optional[Manual]:
    """Find an active manual in an organization by normalized title."""
    return (
        db.query(Manual)
        .filter(
            Manual.org_id == org_id,
            Manual.deleted_at.is_(None),
            Manual.is_active.is_(True),
            func.lower(Manual.title) == title.strip().lower(),
        )
        .first()
    )


def get_by_sha256(db: DbSession, sha256: str) -> Optional[Manual]:
    """Look up an active manual by its content hash.

    Kept for diagnostics/backwards compatibility. Upload deduplication is now
    title-based, so identical PDF bytes may be stored under different active
    titles.
    """
    return db.query(Manual).filter(Manual.sha256 == sha256, Manual.deleted_at.is_(None)).first()


def update_file_metadata(
    db: DbSession,
    manual: Manual,
    *,
    storage_path: str,
    original_filename: str,
    file_size: int,
    sha256: str,
    uploaded_by: int,
    title: Optional[str] = None,
    category_id: Optional[int] = None,
) -> Manual:
    """Replace a manual's file metadata and bump its visible version number."""
    if title is not None:
        manual.title = title
    if category_id is not None:
        manual.category_id = category_id
    manual.storage_path = storage_path
    manual.original_filename = original_filename
    manual.mime_type = "application/pdf"
    manual.file_size = file_size
    manual.sha256 = sha256
    manual.uploaded_by = uploaded_by
    manual.version_number = (manual.version_number or 1) + 1
    db.flush()
    return manual


def soft_delete(db: DbSession, manual: Manual) -> None:
    """Mark a manual unavailable without removing its historical row."""
    manual.deleted_at = datetime.now(timezone.utc)
    manual.is_active = False
    db.flush()


def touch_last_accessed(db: DbSession, manual: Manual) -> None:
    """Update the manual's last-access timestamp after a successful read."""
    manual.last_accessed_at = datetime.now(timezone.utc)
    db.flush()


def cleanup_orphans(db: DbSession) -> list[Manual]:
    """Return manuals stuck in 'pending' storage_path (orphaned uploads)."""
    return (
        db.query(Manual).filter(Manual.storage_path == "pending", Manual.deleted_at.is_(None)).all()
    )


# ── access logs ───────────────────────────────────────────────


def record_access(
    db: DbSession,
    *,
    org_id: int,
    manual_id: int,
    user_id: int,
    action: ManualAction,
    watermark_hash_id: Optional[str] = None,
    ip: Optional[str] = None,
) -> ManualAccessLog:
    """Record a user action against a manual for audit/reporting purposes."""
    log = ManualAccessLog(
        org_id=org_id,
        manual_id=manual_id,
        user_id=user_id,
        action=action,
        watermark_hash_id=watermark_hash_id,
        ip=ip,
    )
    db.add(log)
    db.flush()
    return log
