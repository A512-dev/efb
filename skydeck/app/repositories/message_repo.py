"""Repository helpers for creating, reading, and updating messages."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.message import Message
from app.models.message_attachment import MessageAttachment
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
    """Create and persist a message within an organization."""
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
    """Return a paginated message list and total count for a user's mailbox."""
    query = (
        db.query(Message)
        .options(
            joinedload(Message.sender),
            joinedload(Message.recipient),
            selectinload(Message.attachments),
        )
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
    """Fetch a message if the user belongs to its organization and can view it."""
    return (
        db.query(Message)
        .options(
            joinedload(Message.sender),
            joinedload(Message.recipient),
            selectinload(Message.attachments),
        )
        .filter(
            Message.id == message_id,
            Message.org_id == user.org_id,
            or_(Message.recipient_id == user.id, Message.sender_id == user.id),
        )
        .first()
    )


def mark_read(db: DbSession, message: Message) -> Message:
    """Set a message's read timestamp if it has not already been read."""
    if message.read_at is None:
        message.read_at = datetime.now(timezone.utc)
        db.flush()
    return message


def create_attachment(
    db: DbSession,
    *,
    org_id: int,
    message_id: int,
    storage_path: str,
    original_filename: str,
    mime_type: str,
    file_size: int,
    sha256: str,
    encrypted_key: str,
    key_nonce: str,
    content_nonce: str,
    encryption_key_id: str,
    encryption_alg: str,
) -> MessageAttachment:
    """Create attachment metadata for an encrypted stored object."""
    attachment = MessageAttachment(
        org_id=org_id,
        message_id=message_id,
        storage_path=storage_path,
        original_filename=original_filename,
        mime_type=mime_type,
        file_size=file_size,
        sha256=sha256,
        encrypted_key=encrypted_key,
        key_nonce=key_nonce,
        content_nonce=content_nonce,
        encryption_key_id=encryption_key_id,
        encryption_alg=encryption_alg,
    )
    db.add(attachment)
    db.flush()
    return attachment


def get_attachment_for_message(
    db: DbSession,
    *,
    org_id: int,
    message_id: int,
    attachment_id: int,
) -> Optional[MessageAttachment]:
    """Fetch an attachment by id inside a message and organization."""
    return (
        db.query(MessageAttachment)
        .filter(
            MessageAttachment.org_id == org_id,
            MessageAttachment.message_id == message_id,
            MessageAttachment.id == attachment_id,
        )
        .first()
    )
