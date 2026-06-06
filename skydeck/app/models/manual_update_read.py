"""SQLAlchemy model tracking which users have read manual update events."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ManualUpdateRead(Base):
    """Per-user read state for the manual update feed."""

    __tablename__ = "manual_update_reads"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "manual_update_event_id",
            name="uq_manual_update_reads_user_event",
        ),
        Index("idx_manual_update_reads_org_id", "org_id"),
        Index("idx_manual_update_reads_user_id", "user_id"),
        Index("idx_manual_update_reads_event_id", "manual_update_event_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    manual_update_event_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("manual_update_events.id", ondelete="CASCADE"), nullable=False
    )
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
