"""Pydantic schemas for the user-facing manual-update feed.

``is_read`` and ``read_at`` are computed by joining shared events with the
current user's ``ManualUpdateRead`` rows; they are not columns on the event
itself.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ManualUpdateEventOut(BaseModel):
    """User-specific view of one shared upload/update/delete event."""

    id: int
    org_id: int
    manual_id: Optional[int] = None
    actor_user_id: Optional[int] = None
    action: str
    title: str
    note: Optional[str] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ManualUpdateReadResponse(BaseModel):
    """Response returned after marking one manual update as read."""

    message: str = "Manual update marked as read"
    item: ManualUpdateEventOut


class ManualUpdateReadAllResponse(BaseModel):
    """Response returned after marking all current manual updates as read."""

    message: str = "Manual updates marked as read"
    marked_count: int
