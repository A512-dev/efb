"""Manual read tracking routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.deps import require_roles
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.manual_reads import ManualRead
from app.models.user import User
from app.repositories import manual_reads_repo, manual_repo
from app.schemas.auth import ErrorResponse
from app.schemas.manual_reads import ManualReadOut
from app.services import audit_service

router = APIRouter(prefix="/manuals", tags=["manual-reads"])

_ALL_ROLES = require_roles(
    UserRole.admin,
    UserRole.pilot,
    UserRole.chief_pilot,
    UserRole.safety,
    UserRole.planning,
    UserRole.technical,
)
_ADMIN = require_roles(UserRole.admin)


def _read_out(read: ManualRead) -> ManualReadOut:
    return ManualReadOut(
        id=read.id,
        org_id=read.org_id,
        user_id=read.user_id,
        manual_id=read.manual_id,
        read_at=read.read_at,
        last_read_at=read.last_read_at,
        read_count=read.read_count,
        created_at=read.created_at,
        user_name=read.user.name,
        manual_title=read.manual.title,
    )


@router.get(
    "/reads/me",
    response_model=list[ManualReadOut],
    responses={401: {"model": ErrorResponse}},
    summary="List manuals read by the current user",
)
def list_my_manual_reads(
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    reads = manual_reads_repo.list_for_user(
        db,
        org_id=current_user.org_id,
        user_id=current_user.id,
    )
    return [_read_out(read) for read in reads]


@router.get(
    "/reads",
    response_model=list[ManualReadOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
    summary="List all manual reads in the organization (admin only)",
)
def list_manual_reads(
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    reads = manual_reads_repo.list_for_org(db, org_id=current_user.org_id)
    return [_read_out(read) for read in reads]


@router.post(
    "/{manual_id}/read",
    response_model=ManualReadOut,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Mark a manual as read",
)
def mark_manual_read(
    manual_id: int,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    manual = manual_repo.get_by_id(db, manual_id)
    if manual is None or manual.org_id != current_user.org_id:
        raise NotFoundError("Manual not found")

    read = manual_reads_repo.mark_read(
        db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        manual_id=manual.id,
    )
    audit_service.record(
        db,
        action="manual.read",
        target_type="manual",
        target_id=manual.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
    )
    db.commit()
    db.refresh(read)
    return _read_out(read)
