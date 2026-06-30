"""Repository operations for accumulated manual-read state.

Callers own the transaction. ``mark_read`` flushes so generated IDs and updated
counters are immediately visible, but the route decides whether the surrounding
manual-access workflow should commit or roll back.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import joinedload

from app.models.manual import Manual
from app.models.manual_reads import ManualRead


def mark_read(
    db: DbSession,
    *,
    org_id: int,
    user_id: int,
    manual_id: int,
    manual_title: Optional[str] = None,
) -> ManualRead:
    """Create a first-read marker or update latest timestamp and counter.

    The database unique constraint backs up this application-level upsert
    pattern, ensuring at most one state row per user/manual pair.
    """
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
    if manual_title is None:
        manual_title = db.query(Manual.title).filter(Manual.id == manual_id).scalar() or ""

    if read is None:
        read = ManualRead(
            org_id=org_id,
            user_id=user_id,
            manual_id=manual_id,
            read_at=now,
            last_read_at=now,
            read_count=1,
            is_read=True,
            unread_at=None,
            manual_title=manual_title,
        )
        db.add(read)
    else:
        read.last_read_at = now
        read.read_count += 1
        read.is_read = True
        read.unread_at = None
        read.manual_title = manual_title

    # Flush makes a newly allocated ID available to response construction while
    # retaining the caller's larger transaction boundary.
    db.flush()
    return read


def mark_unread(
    db: DbSession,
    *,
    org_id: int,
    user_id: int,
    manual_id: int,
) -> Optional[ManualRead]:
    """Mark one user's current manual state unread while retaining history."""
    read = (
        db.query(ManualRead)
        .filter(
            ManualRead.org_id == org_id,
            ManualRead.user_id == user_id,
            ManualRead.manual_id == manual_id,
        )
        .first()
    )
    if read is None:
        return None

    read.is_read = False
    read.unread_at = datetime.now(timezone.utc)
    db.flush()
    return read


def mark_manual_unread(db: DbSession, *, org_id: int, manual_id: int) -> int:
    """Clear current-read state for all users after a manual PDF replacement."""
    now = datetime.now(timezone.utc)
    updated_count = (
        db.query(ManualRead)
        .filter(
            ManualRead.org_id == org_id,
            ManualRead.manual_id == manual_id,
            ManualRead.is_read.is_(True),
        )
        .update(
            {
                ManualRead.is_read: False,
                ManualRead.unread_at: now,
            },
            synchronize_session=False,
        )
    )
    db.flush()
    return updated_count


def list_for_user(db: DbSession, *, org_id: int, user_id: int) -> list[ManualRead]:
    """List one user's read states with user/manual display data preloaded."""
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
