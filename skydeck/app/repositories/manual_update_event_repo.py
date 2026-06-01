from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session as DbSession

from app.models.manual_update_event import ManualUpdateEvent


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
    query = db.query(ManualUpdateEvent).filter(ManualUpdateEvent.org_id == org_id)
    total = query.count()
    items = query.order_by(ManualUpdateEvent.created_at.desc()).offset(offset).limit(limit).all()
    return items, total
