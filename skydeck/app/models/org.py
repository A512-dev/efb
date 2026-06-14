"""SQLAlchemy model for tenant organizations."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, Identity, Text, event, func, insert
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.manual import Manual
    from app.models.manual_category import ManualCategory
    from app.models.user import User


class Org(Base):
    """Top-level tenant boundary for users, manuals, and related organization data."""

    __tablename__ = "orgs"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    # settings_json leaves room for tenant-specific options without schema churn.
    settings_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # ── relationships ──────────────────────────────────────
    users: Mapped[list[User]] = relationship(back_populates="org", cascade="all, delete-orphan")
    manuals: Mapped[list[Manual]] = relationship(back_populates="org", cascade="all, delete-orphan")
    manual_categories: Mapped[list[ManualCategory]] = relationship(
        back_populates="org", cascade="all, delete-orphan"
    )


@event.listens_for(Org, "after_insert")
def _create_default_manual_categories(_mapper, connection, target: Org) -> None:
    """Create the default manual category tree for every newly inserted org."""
    from app.models.manual_category import ManualCategory
    from app.services.manual_category_service import DEFAULT_MANUAL_CATEGORY_TREE

    # Insert via the raw connection because ORM sessions are not available inside mapper events.
    for root_order, root_spec in enumerate(DEFAULT_MANUAL_CATEGORY_TREE, start=1):
        root_id = connection.execute(
            insert(ManualCategory.__table__)
            .values(
                org_id=target.id,
                parent_id=None,
                name=root_spec["name"],
                slug=root_spec["slug"],
                sort_order=root_order,
                is_active=True,
            )
            .returning(ManualCategory.id)
        ).scalar_one()

        connection.execute(
            insert(ManualCategory.__table__),
            [
                {
                    "org_id": target.id,
                    "parent_id": root_id,
                    "name": child_name,
                    "slug": child_slug,
                    "sort_order": child_order,
                    "is_active": True,
                }
                for child_order, (child_name, child_slug) in enumerate(
                    root_spec["children"], start=1
                )
            ],
        )
