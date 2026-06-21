"""SQLAlchemy model for revocable refresh-token sessions.

Access JWTs are stateless and short-lived. Refresh tokens are tied to these
database rows so logout, expiration, or administrative revocation can prevent
future access-token issuance.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Index, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.manual_access_log import ManualAccessLog
    from app.models.user import User


class Session(Base):
    """A revocable login session backed by a hashed refresh token.

    A row is usable only while it is unrevoked and before ``expires_at``.
    ``last_seen_at`` records refresh activity without changing the original
    creation timestamp.
    """

    __tablename__ = "sessions"
    __table_args__ = (
        Index("idx_sessions_user_id", "user_id"),
        Index("idx_sessions_expires_at", "expires_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    device_info_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Store only the hash so a database leak does not expose usable refresh tokens.
    refresh_token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── relationships ──────────────────────────────────────
    user: Mapped[User] = relationship(back_populates="sessions")
    access_logs: Mapped[list[ManualAccessLog]] = relationship(back_populates="session")
