"""Pydantic request and response schemas for authentication routes.

Request models validate untrusted JSON before service code sees it. Response
models document the public token contract and prevent ORM/security fields from
being serialized accidentally.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import AircraftType, UserRole, normalize_aircraft_type

# ── requests ──────────────────────────────────────────────────


class LoginRequest(BaseModel):
    """Email/password payload plus optional client device metadata.

    ``EmailStr`` performs syntax validation and ``device_info`` is persisted on
    login/session audit rows when supplied by a client.
    """

    email: EmailStr
    password: str = Field(..., min_length=1)
    device_info: Optional[dict] = None


class RefreshRequest(BaseModel):
    """Payload carrying the raw refresh credential for refresh or logout."""

    refresh_token: str


class SignupRequest(BaseModel):
    """Validated fields required to create a new account.

    The administrator explicitly assigns role, position, and aircraft type.
    Authorization for who may call signup is enforced by the route.
    """

    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole
    position: str = Field(..., min_length=1, max_length=200)
    aircraft_type: AircraftType

    @field_validator("name", "position", mode="before")
    @classmethod
    def _strip_required_text(cls, value: object) -> object:
        """Reject null text and normalize surrounding whitespace."""
        if value is None:
            raise ValueError("Field cannot be null")
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("aircraft_type", mode="before")
    @classmethod
    def _normalize_aircraft_type(cls, value: object) -> object:
        """Accept known legacy labels while storing a canonical fleet value."""
        if value is None:
            raise ValueError("Field cannot be null")
        return normalize_aircraft_type(value)


class PasswordChangeRequest(BaseModel):
    """Schema for new users to set their password using signup key."""

    email: EmailStr
    signup_key: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)

    model_config = {"extra": "forbid"}


class PasswordChangeResponse(BaseModel):
    """Response for successful password change."""

    message: str = "Password changed successfully"


# ── embedded objects ──────────────────────────────────────────


class TokenUserInfo(BaseModel):
    """Small user object embedded in login responses."""

    id: int
    name: str
    role: str


# ── responses ─────────────────────────────────────────────────


class TokenResponse(BaseModel):
    """Token pair returned after successful login.

    The access token authenticates ordinary requests. The longer-lived refresh
    token should be stored more carefully and sent only to the refresh/logout
    endpoints.
    """

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
    role: str
    access_token: str
    refresh_token: str


class ErrorResponse(BaseModel):
    """Standard error payload used in OpenAPI response declarations."""

    error: str
    code: int
