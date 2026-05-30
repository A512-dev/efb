from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Message(Base):
    """Direct message between users inside the same organisation."""

    __tablename__ = "messages"
    __table_args__ = (
        Index("idx_messages_org_id", "org_id"),
        Index("idx_messages_sender_id", "sender_id"),
        Index("idx_messages_recipient_id", "recipient_id"),
        Index("idx_messages_recipient_created", "recipient_id", "created_at"),
        Index("idx_messages_sender_created", "sender_id", "created_at"),
        Index("idx_messages_unread", "recipient_id", postgresql_where="read_at IS NULL"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    sender_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    recipient_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    subject: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
