"""User-specific HTTP view of organization-wide manual update events.

Upload/update/delete actions create shared feed rows in ``manuals.py``. These
routes combine those rows with the current user's independent read markers and
provide idempotent single/all read operations.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.deps import require_roles
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.manual_update_event import ManualUpdateEvent
from app.models.user import User
from app.repositories import manual_update_event_repo
from app.schemas.auth import ErrorResponse
from app.schemas.manual_update_event import (
    ManualUpdateEventOut,
    ManualUpdateReadAllResponse,
    ManualUpdateReadResponse,
)
from app.schemas.pagination import PaginatedResponse
from app.services import audit_service

router = APIRouter(prefix="/manual-updates", tags=["manual-updates"])

_ALL_ROLES = require_roles(
    UserRole.admin,
    UserRole.pilot,
    UserRole.chief_pilot,
    UserRole.safety,
    UserRole.planning,
    UserRole.technical,
)


def _manual_update_out(
    item: ManualUpdateEvent,
    *,
    read_map: dict[int, datetime],
) -> ManualUpdateEventOut:
    """Map a manual update event and the current user's read state."""
    read_at = read_map.get(item.id)
    return ManualUpdateEventOut(
        id=item.id,
        org_id=item.org_id,
        manual_id=item.manual_id,
        actor_user_id=item.actor_user_id,
        action=item.action,
        title=item.title,
        note=item.note,
        is_read=read_at is not None,
        read_at=read_at,
        created_at=item.created_at,
    )


@router.get(
    "",
    response_model=PaginatedResponse[ManualUpdateEventOut],
    responses={401: {"model": ErrorResponse}},
    summary="List manual update feed entries",
)
def list_manual_updates(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    """Return a page of tenant events annotated with the caller's read state."""
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    offset = (page - 1) * limit
    items, total = manual_update_event_repo.list_for_org(
        db,
        org_id=current_user.org_id,
        offset=offset,
        limit=limit,
    )
    # Fetch all read markers for this page in one query, then merge in memory.
    read_map = manual_update_event_repo.get_read_map(
        db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        event_ids=[item.id for item in items],
    )

    return PaginatedResponse(
        page=page,
        limit=limit,
        total=total,
        items=[_manual_update_out(item, read_map=read_map) for item in items],
    )


@router.post(
    "/{event_id}/read",
    response_model=ManualUpdateReadResponse,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Mark one manual update as read",
)
def mark_manual_update_read(
    event_id: int,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    """Idempotently persist read state and audit it for one visible event."""
    item = manual_update_event_repo.get_for_org(
        db,
        org_id=current_user.org_id,
        event_id=event_id,
    )
    if item is None:
        raise NotFoundError("Manual update not found")

    read = manual_update_event_repo.mark_read(
        db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        event_id=item.id,
    )
    audit_service.record(
        db,
        action="manual_update.read",
        target_type="manual_update_event",
        target_id=item.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
    )
    db.commit()

    return ManualUpdateReadResponse(
        item=_manual_update_out(item, read_map={item.id: read.read_at})
    )


@router.post(
    "/read-all",
    response_model=ManualUpdateReadAllResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Mark all current manual updates as read",
)
def mark_all_manual_updates_read(
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    """Create missing markers for every event currently in the tenant feed."""
    marked_count = manual_update_event_repo.mark_all_read(
        db,
        org_id=current_user.org_id,
        user_id=current_user.id,
    )
    audit_service.record(
        db,
        action="manual_update.read_all",
        target_type="manual_update_event",
        target_id="all",
        user_id=current_user.id,
        org_id=current_user.org_id,
        metadata={"marked_count": marked_count},
    )
    db.commit()
    return ManualUpdateReadAllResponse(marked_count=marked_count)
