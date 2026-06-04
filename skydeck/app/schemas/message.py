"""Pydantic schemas for internal messaging routes."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MessageCreateRequest(BaseModel):
    """Create a message.

    Pilots omit recipient_ids so the message is delivered to all admins in
    their organisation. Admins must provide one or more pilot recipient ids.
    """

    body: str = Field(..., min_length=1, max_length=5000)
    subject: Optional[str] = Field(default=None, max_length=200)
    recipient_ids: Optional[list[int]] = None


class MessageUserOut(BaseModel):
    """Compact sender/recipient user object embedded in message responses."""

    id: int
    name: str
    email: str
    role: str

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    """Public message representation with optional sender/recipient details."""

    id: int
    org_id: int
    sender_id: Optional[int] = None
    recipient_id: Optional[int] = None
    subject: Optional[str] = None
    body: str
    read_at: Optional[datetime] = None
    created_at: datetime
    sender: Optional[MessageUserOut] = None
    recipient: Optional[MessageUserOut] = None

    model_config = {"from_attributes": True}


class MessageCreateResponse(BaseModel):
    """Response returned after one request creates one or more messages."""

    message: str = "Message sent successfully"
    items: list[MessageOut]


class MessageReadResponse(BaseModel):
    """Response returned after marking a message as read."""

    message: str = "Message marked as read"
    item: MessageOut
