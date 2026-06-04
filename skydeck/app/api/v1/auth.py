"""Authentication routes: signup, login, refresh, and logout."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session as DbSession

from app.db.session import get_db
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


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=201,
    responses={409: {"model": ErrorResponse}},
    summary="Create a new pilot account",
)
def signup(body: SignupRequest, request: Request, db: DbSession = Depends(get_db)):
    """Register a new user (defaults to pilot role)."""
    result = auth_service.signup(
        db,
        name=body.name,
        email=body.email,
        password=body.password,
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
