from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

# ── requests ──────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)
    device_info: Optional[dict] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


# ── embedded objects ──────────────────────────────────────────


class TokenUserInfo(BaseModel):
    id: int
    name: str
    role: str


# ── responses ─────────────────────────────────────────────────


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: TokenUserInfo


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    message: str = "Logged out successfully"


class SignupResponse(BaseModel):
    user_id: int
    access_token: str
    refresh_token: str


class ErrorResponse(BaseModel):
    error: str
    code: int
