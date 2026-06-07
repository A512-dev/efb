"""SQLAlchemy model for organization-scoped user messages."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Index, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.message_attachment import MessageAttachment


class Message(Base):
    """Direct message between users inside the same organisation."""

    __tablename__ = "messages"
    __table_args__ = (
        Index("idx_messages_org_id", "org_id"),
        Index("idx_messages_sender_id", "sender_id"),
        Index("idx_messages_recipient_id", "recipient_id"),
        Index("idx_messages_recipient_created", "recipient_id", "created_at"),
        Index("idx_messages_sender_created", "sender_id", "created_at"),
        Index("idx_messages_unread", "recipient_id", postgresql_where=text("read_at IS NULL")),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    # Sender/recipient are nullable so deleting a user does not delete the conversation record.
    sender_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    recipient_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    subject: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # Null read_at means the recipient has not opened the message yet.
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    attachments: Mapped[list[MessageAttachment]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
    )

    @property
    def is_read(self) -> bool:
        """Return whether the recipient has opened the message."""
        return self.read_at is not None

    @property
    def read_by_recipient(self) -> bool:
        """Sender-facing read receipt flag derived from read_at."""
        return self.read_at is not None
