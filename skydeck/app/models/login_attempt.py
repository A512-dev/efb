"""SQLAlchemy model for login-attempt security records.

Rows are written for successful and failed attempts, including cases where no
user can be resolved. That is why organization, user, and email are nullable:
the attempted identity may be unknown or malformed.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import CIText


class LoginAttempt(Base):
    """Append-only evidence of one authentication attempt.

    Indexes support security investigations by tenant, user, time, or repeated
    attempts against an email address. ``failure_reason`` should contain a safe
    category, never a password or raw token.
    """

    __tablename__ = "login_attempts"
    __table_args__ = (
        Index("idx_login_attempts_org_id", "org_id"),
        Index("idx_login_attempts_user_id", "user_id"),
        Index("idx_login_attempts_created_at", "created_at"),
        Index("idx_login_attempts_email_created", "email", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    email: Mapped[Optional[str]] = mapped_column(CIText(), nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    device_info_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
