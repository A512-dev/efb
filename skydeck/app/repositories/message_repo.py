from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import joinedload

from app.models.message import Message
from app.models.user import User

MessageBox = Literal["inbox", "sent", "all"]


def create(
    db: DbSession,
    *,
    org_id: int,
    sender_id: int,
    recipient_id: int,
    body: str,
    subject: Optional[str] = None,
) -> Message:
    message = Message(
        org_id=org_id,
        sender_id=sender_id,
        recipient_id=recipient_id,
        subject=subject,
        body=body,
    )
    db.add(message)
    db.flush()
    return message


def list_for_user(
    db: DbSession,
    *,
    user: User,
    box: MessageBox = "inbox",
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[Message], int]:
    query = (
        db.query(Message)
        .options(joinedload(Message.sender), joinedload(Message.recipient))
        .filter(Message.org_id == user.org_id)
    )

    if box == "inbox":
        query = query.filter(Message.recipient_id == user.id)
    elif box == "sent":
        query = query.filter(Message.sender_id == user.id)
    else:
        query = query.filter(or_(Message.recipient_id == user.id, Message.sender_id == user.id))

    total = query.count()
    items = query.order_by(Message.created_at.desc()).offset(offset).limit(limit).all()
    return items, total


def get_visible_to_user(db: DbSession, *, message_id: int, user: User) -> Optional[Message]:
    return (
        db.query(Message)
        .options(joinedload(Message.sender), joinedload(Message.recipient))
        .filter(
            Message.id == message_id,
            Message.org_id == user.org_id,
            or_(Message.recipient_id == user.id, Message.sender_id == user.id),
        )
        .first()
    )


def mark_read(db: DbSession, message: Message) -> Message:
    if message.read_at is None:
        message.read_at = datetime.now(timezone.utc)
        db.flush()
    return message
