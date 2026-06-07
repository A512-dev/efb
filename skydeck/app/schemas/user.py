"""Pydantic schemas for user profile responses."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserMeResponse(BaseModel):
    """Current authenticated user profile."""

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
