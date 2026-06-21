"""SQLAlchemy model tracking which users have read which manuals."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.manual import Manual
    from app.models.user import User


class ManualRead(Base):
    """One user's accumulated read state for one manual."""

    __tablename__ = "manual_reads"
    __table_args__ = (
        UniqueConstraint("user_id", "manual_id", name="uq_manual_reads_user_manual"),
        Index("idx_manual_reads_org_id", "org_id"),
        Index("idx_manual_reads_manual_id", "manual_id"),
        Index("idx_manual_reads_user_id", "user_id"),
        Index("idx_manual_reads_last_read_at", "last_read_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    manual_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("manuals.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    read_count: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    manual: Mapped[Manual] = relationship(back_populates="reads")
    user: Mapped[User] = relationship(back_populates="manual_reads")
