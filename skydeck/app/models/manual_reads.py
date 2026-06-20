"""SQLAlchemy model tracking which users have read which documents."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ManualAction

if TYPE_CHECKING:
    from app.models.manual import Manual
    from app.models.session import Session


class ManualReads(Base):
    """Tracks which users have read which manuals, for audit and analytics purposes."""

    __tablename__ = "manual_reads"
    __table_args__ = (
        Index("idx_manual_reads_org_id", "org_id"),
        Index("idx_manual_reads_manual_id", "manual_id"),
        Index("idx_manual_reads_user_id", "user_id"),
        Index("idx_manual_reads_session_id", "session_id"),
        Index("idx_manual_reads_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="SET NULL"), nullable=True
    )
    manual_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("manuals.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    read_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # TODO:Add indexes like:
    #     idx_manual_reads_org_id
    #     idx_manual_reads_user_id
    #     idx_manual_reads_manual_id
    #     idx_manual_reads_user_manual

    # TODO: add a unique constraint:
    #     uq_manual_reads_user_manual (user_id, manual_id)

    # ── relationships ──────────────────────────────────────
    manual: Mapped[Optional[Manual]] = relationship(back_populates="reads")
    user: Mapped[Optional[Session]] = relationship(back_populates="manual_reads")
    
