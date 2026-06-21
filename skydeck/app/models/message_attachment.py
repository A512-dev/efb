"""SQLAlchemy metadata for encrypted files attached to messages.

The ciphertext is stored through a ``StorageProvider``. This row stores the
path plus envelope-encryption metadata needed to recover the per-file data key;
plaintext file bytes and plaintext keys never enter the database.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.message import Message


class MessageAttachment(Base):
    """Storage, integrity, and envelope-encryption metadata for one file.

    ``sha256`` describes plaintext contents for integrity checks. The three
    nonce/key fields are not secrets by themselves but must match the encrypted
    object and configured master key for authenticated decryption to succeed.
    """

    __tablename__ = "message_attachments"
    __table_args__ = (
        CheckConstraint("file_size >= 0", name="ck_message_attachments_file_size"),
        Index("idx_message_attachments_org_id", "org_id"),
        Index("idx_message_attachments_message_id", "message_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False
    )
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    original_filename: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mime_type: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_key: Mapped[str] = mapped_column(Text, nullable=False)
    key_nonce: Mapped[str] = mapped_column(Text, nullable=False)
    content_nonce: Mapped[str] = mapped_column(Text, nullable=False)
    encryption_key_id: Mapped[str] = mapped_column(Text, nullable=False)
    encryption_alg: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    message: Mapped[Message] = relationship(back_populates="attachments")
