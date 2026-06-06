"""Pydantic schemas for manual update feed responses."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ManualUpdateEventOut(BaseModel):
    """User-facing summary of one manual upload/update/delete event."""

    id: int
    org_id: int
    manual_id: Optional[int] = None
    actor_user_id: Optional[int] = None
    action: str
    title: str
    note: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
