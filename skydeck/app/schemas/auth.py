"""Pydantic request and response schemas for authentication routes."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

# ── requests ──────────────────────────────────────────────────


class LoginRequest(BaseModel):
    """Email/password payload plus optional client device metadata."""

    email: EmailStr
    password: str = Field(..., min_length=1)
    device_info: Optional[dict] = None


class RefreshRequest(BaseModel):
    """Payload carrying a refresh token for refresh/logout operations."""

    refresh_token: str


class SignupRequest(BaseModel):
    """New account payload; service layer assigns the default role."""

    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


# ── embedded objects ──────────────────────────────────────────


class TokenUserInfo(BaseModel):
    """Small user object embedded in login responses."""

    id: int
    name: str
    role: str


# ── responses ─────────────────────────────────────────────────


class TokenResponse(BaseModel):
    """Token pair returned after successful login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: TokenUserInfo


class RefreshResponse(BaseModel):
    """New access token returned after refresh-token validation."""

    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    """Confirmation payload returned after logout."""

    message: str = "Logged out successfully"


class SignupResponse(BaseModel):
    """Signup response containing the created user id and token pair."""

    user_id: int
    access_token: str
    refresh_token: str


class ErrorResponse(BaseModel):
    """Standard error payload used in OpenAPI response declarations."""

    error: str
    code: int
