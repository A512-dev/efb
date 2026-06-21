"""SQLAlchemy model for general application audit events.

This is the flexible catch-all audit stream. Features with specialized query
needs may use their own tables (for example ``manual_access_logs``), while
``AuditLog`` records broader administrative and system actions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLog(Base):
    """Generic audit event not covered by a specialized history table.

    Organization and user foreign keys use ``SET NULL`` so deleting an actor or
    tenant does not erase evidence that an action occurred. Human-readable
    ``action``/``target_*`` columns support ordinary queries, while the JSONB
    columns preserve optional structured context.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_logs_org_id", "org_id"),
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # ``action`` is a verb such as "seed", "manual.upload", or "user.delete".
    action: Mapped[str] = mapped_column(Text, nullable=False)
    target_type: Mapped[str] = mapped_column(Text, nullable=False)
    target_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    # JSONB keeps request/device context queryable without forcing every
    # feature-specific detail into a permanent column.
    device_info_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
