#skydeck\app\api\v1\auth.py
"""HTTP boundary for signup, login, refresh, and logout.

These handlers validate request/response shapes and collect request context,
then delegate authentication transactions to :mod:`app.services.auth_service`.
They never manipulate password hashes, JWT claims, or session rows directly.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session as DbSession

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import (
    ErrorResponse,
    LoginRequest,
    LogoutResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
    RefreshRequest,
    RefreshResponse,
    SignupRequest,
    SignupResponse,
    TokenResponse,
)
from app.services import auth_service

# ``app.main`` adds /api/v1; this router contributes the /auth segment.
router = APIRouter(prefix="/auth", tags=["auth"])
# Build the reusable role dependency once. FastAPI executes the returned inner
# function for each protected request.
_ADMIN = require_roles(UserRole.admin)


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=201,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Create a new user account (admin only)",
)
def signup(
    body: SignupRequest,
    request: Request,
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    """Register a user inside the authenticated admin's organization.

    The route supplies the admin as both tenant boundary and audit actor, so a
    caller cannot choose an arbitrary organization in the JSON body.
    """
    result = auth_service.signup(
        db,
        name=body.name,
        email=body.email,
        password=body.password,
        role=body.role,
        position=body.position,
        aircraft_type=body.aircraft_type,
        org_id=current_user.org_id,
        actor_user_id=current_user.id,
        ip=request.client.host if request.client else None,
    )
    return SignupResponse(**result)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Authenticate and receive tokens",
)
def login(body: LoginRequest, request: Request, db: DbSession = Depends(get_db)):
    """Validate credentials, create a persisted session, and return tokens."""
    result = auth_service.login(
        db,
        email=body.email,
        password=body.password,
        ip=request.client.host if request.client else None,
        device_info=body.device_info,
    )
    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        user=result["user"],
    )


@router.post(
    "/change-password",
    response_model=PasswordChangeResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Set initial password using signup key",
)
def change_password(
    body: PasswordChangeRequest,
    db: DbSession = Depends(get_db),
):
    """Replace a user's password after validating the shared signup key.

    The endpoint is unauthenticated and does not enforce one-time use.
    """
    auth_service.change_initial_password(
        db,
        email=body.email,
        signup_key=body.signup_key,
        new_password=body.new_password,
    )
    return PasswordChangeResponse()


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Exchange refresh token for a new access token",
)
def refresh_token(body: RefreshRequest, db: DbSession = Depends(get_db)):
    """Issue a replacement access token without rotating the refresh token."""
    result = auth_service.refresh(db, raw_refresh_token=body.refresh_token)
    return RefreshResponse(access_token=result["access_token"])


@router.post(
    "/logout",
    response_model=LogoutResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Revoke the current session",
)
def logout(body: RefreshRequest, db: DbSession = Depends(get_db)):
    """Revoke refresh state; repeated/unknown-token logout remains harmless."""
    auth_service.logout(db, raw_refresh_token=body.refresh_token)
    return LogoutResponse()
