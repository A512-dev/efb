from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories import form_repo
from app.schemas.auth import ErrorResponse
from app.schemas.form import ActiveFormOut

router = APIRouter(prefix="/forms", tags=["forms"])


@router.get(
    "/active",
    response_model=list[ActiveFormOut],
    responses={401: {"model": ErrorResponse}},
    summary="Get current active form schemas",
)
def get_active_forms(
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Return the latest version of every form template for the user's org."""
    rows = form_repo.get_active_forms(db, org_id=current_user.org_id)
    return [ActiveFormOut(**r) for r in rows]
