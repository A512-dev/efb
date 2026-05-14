from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session as DbSession

from app.models.enums import ManualAction
from app.models.manual import Manual
from app.models.manual_access_log import ManualAccessLog

# ── manuals CRUD ──────────────────────────────────────────────


def create(
    db: DbSession,
    *,
    org_id: int,
    title: str,
    storage_path: str,
    original_filename: Optional[str] = None,
    mime_type: Optional[str] = None,
    file_size: Optional[int] = None,
    sha256: Optional[str] = None,
    uploaded_by: Optional[int] = None,
) -> Manual:
    manual = Manual(
        org_id=org_id,
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


def list_active(db: DbSession, *, org_id: int) -> list[Manual]:
    return (
        db.query(Manual)
        .filter(Manual.org_id == org_id, Manual.deleted_at.is_(None), Manual.is_active.is_(True))
        .order_by(Manual.created_at.desc())
        .all()
    )


def get_by_id(db: DbSession, manual_id: int) -> Optional[Manual]:
    return db.query(Manual).filter(Manual.id == manual_id, Manual.deleted_at.is_(None)).first()


def get_by_sha256(db: DbSession, sha256: str) -> Optional[Manual]:
    """Look up an active manual by its content hash for deduplication."""
    return db.query(Manual).filter(Manual.sha256 == sha256, Manual.deleted_at.is_(None)).first()


def soft_delete(db: DbSession, manual: Manual) -> None:
    manual.deleted_at = datetime.now(timezone.utc)
    manual.is_active = False
    db.flush()


def touch_last_accessed(db: DbSession, manual: Manual) -> None:
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
