from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ManualUpdateEvent(Base):
    """User-facing update feed entry for manual upload/update/delete actions."""

    __tablename__ = "manual_update_events"
    __table_args__ = (
        Index("idx_manual_update_events_org_id", "org_id"),
        Index("idx_manual_update_events_manual_id", "manual_id"),
        Index("idx_manual_update_events_actor_user_id", "actor_user_id"),
        Index("idx_manual_update_events_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    manual_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("manuals.id", ondelete="SET NULL"), nullable=True
    )
    actor_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    old_storage_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_storage_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    old_sha256: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_sha256: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    old_version_number: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    new_version_number: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    actor = relationship("User", foreign_keys=[actor_user_id])
    manual = relationship("Manual", foreign_keys=[manual_id])
