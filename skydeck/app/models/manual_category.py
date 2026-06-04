from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Identity, Index, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.manual import Manual
    from app.models.org import Org


class ManualCategory(Base):
    """Hierarchical, organisation-scoped category used to build manual paths."""

    __tablename__ = "manual_categories"
    __table_args__ = (
        Index("idx_manual_categories_org_id", "org_id"),
        Index("idx_manual_categories_parent_id", "parent_id"),
        Index("idx_manual_categories_active", "org_id", "is_active"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("manual_categories.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    org: Mapped[Org] = relationship(back_populates="manual_categories")
    parent: Mapped[Optional[ManualCategory]] = relationship(
        remote_side="ManualCategory.id",
        back_populates="children",
    )
    children: Mapped[list[ManualCategory]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    manuals: Mapped[list[Manual]] = relationship(back_populates="category")
