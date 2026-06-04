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
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
