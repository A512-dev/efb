"""Pydantic schemas and normalization for user profiles.

Update fields are optional so clients can PATCH only selected values, but any
field that is present may not be null. Response models are explicit allowlists
that omit password hashes and soft-deletion metadata.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class UserProfileUpdateRequest(BaseModel):
    """Partial profile update accepted from the current authenticated user."""

    employee_no: Optional[str] = Field(default=None, min_length=1, max_length=100)
    position: Optional[str] = Field(default=None, min_length=1, max_length=200)
    aircraft_type: Optional[str] = Field(default=None, min_length=1, max_length=100)
    medical_expires_at: Optional[datetime] = None
    passport_expires_at: Optional[datetime] = None
    license_expires_at: Optional[datetime] = None

    @field_validator("employee_no", "position", "aircraft_type", mode="before")
    @classmethod
    def _strip_required_text(cls, value: object) -> object:
        """Reject explicit nulls and normalize surrounding whitespace."""
        if value is None:
            raise ValueError("Field cannot be null")
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator(
        "medical_expires_at",
        "passport_expires_at",
        "license_expires_at",
        mode="before",
    )
    @classmethod
    def _parse_date_only_as_datetime(cls, value: object) -> object:
        """Treat ISO date-only input as midnight UTC for API convenience."""
        if value is None:
            raise ValueError("Field cannot be null")
        if isinstance(value, str) and "T" not in value and " " not in value:
            parsed = date.fromisoformat(value)
            return datetime.combine(parsed, time.min, tzinfo=timezone.utc)
        return value

    # Reject misspelled/unknown fields instead of silently ignoring a client's
    # intended update.
    model_config = {"extra": "forbid"}


class UserMeResponse(BaseModel):
    """Complete safe profile returned to the current authenticated user."""

    id: int
    org_id: int
    name: str
    email: str
    role: str
    employee_no: str
    position: str
    aircraft_type: str
    medical_expires_at: datetime
    passport_expires_at: datetime
    license_expires_at: datetime
    profile_picture_id: Optional[int] = None
    profile_picture_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserListItemResponse(BaseModel):
    """Admin-safe organization user row with no authentication secrets."""

    id: int
    org_id: int
    name: str
    email: str
    role: str
    employee_no: str
    position: str
    aircraft_type: str
    medical_expires_at: datetime
    passport_expires_at: datetime
    license_expires_at: datetime
    profile_picture_id: Optional[int] = None
    profile_picture_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserDeleteResponse(BaseModel):
    """Response after a user has been deactivated."""

    message: str = "User deleted successfully"
