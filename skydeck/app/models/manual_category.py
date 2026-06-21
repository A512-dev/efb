"""SQLAlchemy model for hierarchical manual categories.

Categories form an adjacency-list tree: each row points to its optional parent.
Root and sibling slug uniqueness is enforced with separate partial indexes,
allowing the same slug to appear under different branches.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Identity, Index, Integer, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.manual import Manual
    from app.models.org import Org


class ManualCategory(Base):
    """Organization-scoped node used to build manual navigation paths.

    The self-referential ``parent``/``children`` relationships let code walk in
    either direction. Deleting a parent cascades to descendants, while manuals
    use ``RESTRICT`` so a category containing documents cannot vanish silently.
    """

    __tablename__ = "manual_categories"
    __table_args__ = (
        Index("idx_manual_categories_org_id", "org_id"),
        Index("idx_manual_categories_parent_id", "parent_id"),
        Index("idx_manual_categories_active", "org_id", "is_active"),
        Index(
            "uq_manual_categories_root_slug",
            "org_id",
            "slug",
            unique=True,
            postgresql_where=text("parent_id IS NULL"),
        ),
        Index(
            "uq_manual_categories_child_slug",
            "org_id",
            "parent_id",
            "slug",
            unique=True,
            postgresql_where=text("parent_id IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    # parent_id creates the tree; null means this category is a root.
    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("manual_categories.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False)
    # sort_order keeps API responses stable before falling back to alphabetical names.
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # ``remote_side`` tells SQLAlchemy which copy of the self-join is the
    # parent. ``delete-orphan`` treats children removed from the tree as rows
    # that should be deleted.
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
