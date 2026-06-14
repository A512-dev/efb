"""Authentication routes: signup, login, refresh, and logout."""

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
    RefreshRequest,
    RefreshResponse,
    SignupRequest,
    SignupResponse,
    TokenResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
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
    """Register a new user in the current admin's organization."""
    result = auth_service.signup(
        db,
        name=body.name,
        email=body.email,
        password=body.password,
        role=body.role,
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
    """Validate email/password, create a session, and return tokens."""
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
    "/refresh",
    response_model=RefreshResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Exchange refresh token for a new access token",
)
def refresh_token(body: RefreshRequest, db: DbSession = Depends(get_db)):
    """Validate a refresh token and issue a replacement access token."""
    result = auth_service.refresh(db, raw_refresh_token=body.refresh_token)
    return RefreshResponse(access_token=result["access_token"])


@router.post(
    "/logout",
    response_model=LogoutResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Revoke the current session",
)
def logout(body: RefreshRequest, db: DbSession = Depends(get_db)):
    """Revoke the refresh-token session so it cannot be used again."""
    auth_service.logout(db, raw_refresh_token=body.refresh_token)
    return LogoutResponse()
