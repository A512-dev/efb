"""Repository operations for accumulated manual-read state.

Callers own the transaction. ``mark_read`` flushes so generated IDs and updated
counters are immediately visible, but the route decides whether the surrounding
manual-access workflow should commit or roll back.
"""

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

    # Flush makes a newly allocated ID available to response construction while
    # retaining the caller's larger transaction boundary.
    db.flush()
    return read


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
