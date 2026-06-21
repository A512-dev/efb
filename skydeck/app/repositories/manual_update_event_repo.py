"""Persistence for manual-update feed events and per-user read markers.

Events are shared organization-wide. Separate ``ManualUpdateRead`` rows model
each user's view, allowing listing code to merge one event page with a compact
mapping of read timestamps.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session as DbSession

from app.models.manual_update_event import ManualUpdateEvent
from app.models.manual_update_read import ManualUpdateRead


def create(
    db: DbSession,
    *,
    org_id: int,
    manual_id: Optional[int],
    actor_user_id: Optional[int],
    action: str,
    title: str,
    note: Optional[str] = None,
    old_storage_path: Optional[str] = None,
    new_storage_path: Optional[str] = None,
    old_sha256: Optional[str] = None,
    new_sha256: Optional[str] = None,
    old_version_number: Optional[int] = None,
    new_version_number: Optional[int] = None,
) -> ManualUpdateEvent:
    """Create and persist a new manual update event.

    Args:
        db: Database session.
        org_id: Organization identifier.
        manual_id: Optional manual identifier associated with the event.
        actor_user_id: Optional user identifier who performed the action.
        action: Action name describing the event.
        title: Event title.
        note: Optional free-form event note.
        old_storage_path: Optional previous storage path.
        new_storage_path: Optional new storage path.
        old_sha256: Optional previous SHA256 digest.
        new_sha256: Optional new SHA256 digest.
        old_version_number: Optional previous version number.
        new_version_number: Optional new version number.

    Returns:
        The created ManualUpdateEvent instance.
    """
    event = ManualUpdateEvent(
        org_id=org_id,
        manual_id=manual_id,
        actor_user_id=actor_user_id,
        action=action,
        title=title,
        note=note,
        old_storage_path=old_storage_path,
        new_storage_path=new_storage_path,
        old_sha256=old_sha256,
        new_sha256=new_sha256,
        old_version_number=old_version_number,
        new_version_number=new_version_number,
    )
    db.add(event)
    db.flush()
    return event


def list_for_org(
    db: DbSession,
    *,
    org_id: int,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[ManualUpdateEvent], int]:
    """List manual update events for an organization.

    Args:
        db: Database session.
        org_id: Organization identifier.
        offset: Pagination offset.
        limit: Maximum number of events to return.

    Returns:
        A tuple of the event list and the total event count.
    """
    query = db.query(ManualUpdateEvent).filter(ManualUpdateEvent.org_id == org_id)
    total = query.count()
    items = query.order_by(ManualUpdateEvent.created_at.desc()).offset(offset).limit(limit).all()
    return items, total


def get_for_org(
    db: DbSession,
    *,
    org_id: int,
    event_id: int,
) -> Optional[ManualUpdateEvent]:
    """Fetch one manual update event inside an organization."""
    return (
        db.query(ManualUpdateEvent)
        .filter(ManualUpdateEvent.org_id == org_id, ManualUpdateEvent.id == event_id)
        .first()
    )


def get_read_map(
    db: DbSession,
    *,
    org_id: int,
    user_id: int,
    event_ids: list[int],
) -> dict[int, datetime]:
    """Return read timestamps keyed by event ID for efficient response merging.

    A dictionary avoids repeated database queries or linear searches while API
    code annotates a page of events.
    """
    if not event_ids:
        return {}

    reads = (
        db.query(ManualUpdateRead)
        .filter(
            ManualUpdateRead.org_id == org_id,
            ManualUpdateRead.user_id == user_id,
            ManualUpdateRead.manual_update_event_id.in_(event_ids),
        )
        .all()
    )
    return {read.manual_update_event_id: read.read_at for read in reads}


def mark_read(
    db: DbSession,
    *,
    org_id: int,
    user_id: int,
    event_id: int,
) -> ManualUpdateRead:
    """Idempotently create a read marker for one event and user."""
    existing = (
        db.query(ManualUpdateRead)
        .filter(
            ManualUpdateRead.org_id == org_id,
            ManualUpdateRead.user_id == user_id,
            ManualUpdateRead.manual_update_event_id == event_id,
        )
        .first()
    )
    if existing is not None:
        return existing

    read = ManualUpdateRead(org_id=org_id, user_id=user_id, manual_update_event_id=event_id)
    db.add(read)
    db.flush()
    return read


def mark_all_read(
    db: DbSession,
    *,
    org_id: int,
    user_id: int,
) -> int:
    """Create only missing read markers for all current organization events.

    The return value counts new markers rather than total events, which lets the
    API report whether this call actually changed state.
    """
    event_ids = [
        row[0]
        for row in db.query(ManualUpdateEvent.id)
        .filter(ManualUpdateEvent.org_id == org_id)
        .all()
    ]
    read_map = get_read_map(db, org_id=org_id, user_id=user_id, event_ids=event_ids)

    created_count = 0
    for event_id in event_ids:
        if event_id in read_map:
            continue
        db.add(ManualUpdateRead(org_id=org_id, user_id=user_id, manual_update_event_id=event_id))
        created_count += 1

    if created_count:
        db.flush()
    return created_count
