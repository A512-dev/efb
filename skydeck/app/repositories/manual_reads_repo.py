"""Repository helpers for accumulated manual read state."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import joinedload

from app.models.manual_reads import ManualRead


def mark_read(
    db: DbSession,
    *,
    org_id: int,
    user_id: int,
    manual_id: int,
) -> ManualRead:
    """Create a read marker or update its timestamp and counter."""
    read = (
        db.query(ManualRead)
        .filter(
            ManualRead.org_id == org_id,
            ManualRead.user_id == user_id,
            ManualRead.manual_id == manual_id,
        )
        .first()
    )
    now = datetime.now(timezone.utc)
    if read is None:
        read = ManualRead(
            org_id=org_id,
            user_id=user_id,
            manual_id=manual_id,
            read_at=now,
            last_read_at=now,
            read_count=1,
        )
        db.add(read)
    else:
        read.last_read_at = now
        read.read_count += 1

    db.flush()
    return read


def list_for_user(db: DbSession, *, org_id: int, user_id: int) -> list[ManualRead]:
    """List manuals read by one user in their organization."""
    return (
        db.query(ManualRead)
        .options(joinedload(ManualRead.manual), joinedload(ManualRead.user))
        .filter(ManualRead.org_id == org_id, ManualRead.user_id == user_id)
        .order_by(ManualRead.last_read_at.desc())
        .all()
    )


def list_for_org(db: DbSession, *, org_id: int) -> list[ManualRead]:
    """List all user/manual read relationships for an organization."""
    return (
        db.query(ManualRead)
        .options(joinedload(ManualRead.manual), joinedload(ManualRead.user))
        .filter(ManualRead.org_id == org_id)
        .order_by(ManualRead.last_read_at.desc())
        .all()
    )
