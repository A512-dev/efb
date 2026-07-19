"""Per-user markup stored separately from canonical manual PDF bytes."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.manual import Manual
    from app.models.user import User


class ManualAnnotation(Base):
    """One private annotation owned by one user on one manual version."""

    __tablename__ = "manual_annotations"
    __table_args__ = (
        CheckConstraint(
            "annotation_type IN ("
            "'highlight', 'underline', 'strikeout', 'sticky_note', "
            "'ink', 'rectangle', 'ellipse', 'line'"
            ")",
            name="ck_manual_annotations_type",
        ),
        CheckConstraint("manual_version_number >= 1", name="ck_manual_annotations_version"),
        CheckConstraint("page_number >= 1", name="ck_manual_annotations_page"),
        Index("idx_manual_annotations_org_id", "org_id"),
        Index("idx_manual_annotations_user_id", "user_id"),
        Index("idx_manual_annotations_manual_id", "manual_id"),
        Index(
            "idx_manual_annotations_user_manual_version_active",
            "user_id",
            "manual_id",
            "manual_version_number",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    manual_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("manuals.id", ondelete="CASCADE"), nullable=False
    )
    manual_version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    annotation_type: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    geometry_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    style_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    selected_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    note_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    manual: Mapped[Manual] = relationship(back_populates="annotations")
    user: Mapped[User] = relationship(back_populates="manual_annotations")
