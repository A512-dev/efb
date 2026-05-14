from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.manual_access_log import ManualAccessLog
    from app.models.org import Org
    from app.models.user import User


class Manual(Base):
    __tablename__ = "manuals"
    __table_args__ = (
        CheckConstraint("file_size >= 0", name="ck_manuals_file_size"),
        CheckConstraint("version_number >= 1", name="ck_manuals_version_number"),
        Index("idx_manuals_org_id", "org_id"),
        Index("idx_manuals_uploaded_by", "uploaded_by"),
        Index("idx_manuals_sha256", "sha256"),
        Index("idx_manuals_active", "id", postgresql_where=text("deleted_at IS NULL")),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    original_filename: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    sha256: Mapped[Optional[str]] = mapped_column(Text, nullable=True, unique=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── relationships ──────────────────────────────────────
    org: Mapped[Org] = relationship(back_populates="manuals")
    uploaded_by_user: Mapped[Optional[User]] = relationship(back_populates="uploaded_manuals")
    access_logs: Mapped[list[ManualAccessLog]] = relationship(back_populates="manual")
