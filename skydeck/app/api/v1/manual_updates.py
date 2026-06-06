"""Manual update feed routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories import manual_update_event_repo
from app.schemas.auth import ErrorResponse
from app.schemas.manual_update_event import ManualUpdateEventOut
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/manual-updates", tags=["manual-updates"])

_ALL_ROLES = require_roles(
    UserRole.admin,
    UserRole.pilot,
    UserRole.chief_pilot,
    UserRole.safety,
    UserRole.planning,
    UserRole.technical,
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
    """Return update-feed entries scoped to the current user's organization."""
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

    return PaginatedResponse(
        page=page,
        limit=limit,
        total=total,
        items=[ManualUpdateEventOut.model_validate(item) for item in items],
    )
