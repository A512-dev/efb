"""SQLAlchemy metadata for encrypted user profile pictures.

This uses the same envelope-encryption pattern as message attachments but a
different authenticated-data domain, preventing ciphertext from one feature
being substituted into the other.
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
    from app.models.user import User


class UserProfilePicture(Base):
    """Storage and envelope-encryption metadata for one user's image.

    ``User.profile_picture_id`` identifies the current picture. Older metadata
    can be replaced transactionally and its external ciphertext cleaned up
    after the new picture is safely stored.
    """

    __tablename__ = "user_profile_pictures"
    __table_args__ = (
        CheckConstraint("file_size >= 0", name="ck_user_profile_pictures_file_size"),
        Index("idx_user_profile_pictures_org_id", "org_id"),
        Index("idx_user_profile_pictures_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
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

    user: Mapped[User] = relationship("User", foreign_keys=[user_id])
