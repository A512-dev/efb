"""SQLAlchemy model for manual view/download audit entries."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Identity, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ManualAction

if TYPE_CHECKING:
    from app.models.manual import Manual
    from app.models.session import Session


class ManualAccessLog(Base):
    """Append-only access event for manual viewing and downloading."""

    __tablename__ = "manual_access_logs"
    __table_args__ = (
        Index("idx_access_logs_org_id", "org_id"),
        Index("idx_access_logs_manual_id", "manual_id"),
        Index("idx_access_logs_user_id", "user_id"),
        Index("idx_access_logs_session_id", "session_id"),
        Index("idx_access_logs_created_at", "created_at"),
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
    session_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[ManualAction] = mapped_column(
        Enum(ManualAction, name="manual_action", create_constraint=False, native_enum=True),
        nullable=False,
    )
    # watermark_hash_id connects a served PDF copy back to this access event.
    watermark_hash_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    device_info_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # ── relationships ──────────────────────────────────────
    manual: Mapped[Optional[Manual]] = relationship(back_populates="access_logs")
    session: Mapped[Optional[Session]] = relationship(back_populates="access_logs")
