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
    id: int
    name: str
    email: str
    role: str

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
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
    message: str = "Message sent successfully"
    items: list[MessageOut]


class MessageReadResponse(BaseModel):
    message: str = "Message marked as read"
    item: MessageOut
