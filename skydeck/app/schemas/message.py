"""Pydantic schemas for internal messaging routes.

The models support both JSON-only sends and multipart sends with attachments.
A single request may create several recipient-specific ``Message`` rows, which
is why create responses contain a list of items.
"""

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


class MessageAttachmentOut(BaseModel):
    """Safe attachment metadata; encryption internals and paths stay private."""

    id: int
    original_filename: Optional[str] = None
    mime_type: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    """Public message representation with users, receipts, and attachments."""

    id: int
    org_id: int
    sender_id: Optional[int] = None
    recipient_id: Optional[int] = None
    subject: Optional[str] = None
    body: str
    is_read: bool
    read_by_recipient: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    sender: Optional[MessageUserOut] = None
    recipient: Optional[MessageUserOut] = None
    # Pydantic copies model defaults, but this field conceptually represents an
    # empty collection when a message has no attachments.
    attachments: list[MessageAttachmentOut] = []

    model_config = {"from_attributes": True}


class MessageRecipientOut(BaseModel):
    """Admin-selectable recipient summary."""

    id: int
    name: str
    email: str
    role: str
    employee_no: str
    position: str
    aircraft_type: str

    model_config = {"from_attributes": True}


class MessageCreateResponse(BaseModel):
    """Response returned after one request creates one or more messages."""

    message: str = "Message sent successfully"
    items: list[MessageOut]


class MessageReadResponse(BaseModel):
    """Response returned after marking a message as read."""

    message: str = "Message marked as read"
    item: MessageOut
