"""SQLAlchemy model for uploaded operational manuals.

The database stores searchable metadata and the storage-provider path; the PDF
bytes live outside PostgreSQL. Updating a manual replaces that external object
and increments ``version_number`` while retaining one logical manual row.
"""

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
    event,
    func,
    select,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.manual_access_log import ManualAccessLog
    from app.models.manual_annotation import ManualAnnotation
    from app.models.manual_category import ManualCategory
    from app.models.manual_reads import ManualRead
    from app.models.org import Org
    from app.models.user import User


class Manual(Base):
    """A versioned PDF/manual file owned by an organization and category.

    ``deleted_at`` implements soft deletion for auditability. Most user-facing
    repository queries filter it out, while cleanup and history code can still
    find the row. The checksum identifies exact file contents independently of
    title, path, and version metadata.
    """

    __tablename__ = "manuals"
    __table_args__ = (
        CheckConstraint("file_size >= 0", name="ck_manuals_file_size"),
        CheckConstraint("version_number >= 1", name="ck_manuals_version_number"),
        Index("idx_manuals_org_id", "org_id"),
        Index("idx_manuals_category_id", "category_id"),
        Index("idx_manuals_uploaded_by", "uploaded_by"),
        Index("idx_manuals_sha256", "sha256"),
        Index("idx_manuals_active", "id", postgresql_where=text("deleted_at IS NULL")),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("manual_categories.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    # storage_path points to the file backend; the database stores metadata only.
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    original_filename: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    sha256: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # ``is_active`` is a business-state flag; ``deleted_at`` is deletion
    # history. Normal active-library queries require both states to be valid.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    # deleted_at enables soft deletion so audit logs and historical references stay intact.
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── relationships ──────────────────────────────────────
    org: Mapped[Org] = relationship(back_populates="manuals")
    category: Mapped[ManualCategory] = relationship(back_populates="manuals")
    uploaded_by_user: Mapped[Optional[User]] = relationship(back_populates="uploaded_manuals")
    access_logs: Mapped[list[ManualAccessLog]] = relationship(back_populates="manual")
    reads: Mapped[list[ManualRead]] = relationship(back_populates="manual")
    annotations: Mapped[list[ManualAnnotation]] = relationship(back_populates="manual")


@event.listens_for(Manual, "before_insert")
def _assign_fallback_category(_mapper, connection, target: Manual) -> None:
    """Assign Iranair / General when legacy/demo code omits category_id.

    API uploads still require an explicit leaf category. This fallback exists
    only to keep old seed scripts and internal inserts compatible.
    """
    # New API traffic always supplies a category, so the normal path exits
    # immediately without issuing either fallback query.
    if target.category_id is not None:
        return

    from app.models.manual_category import ManualCategory

    root_id = connection.execute(
        select(ManualCategory.id).where(
            ManualCategory.org_id == target.org_id,
            ManualCategory.parent_id.is_(None),
            ManualCategory.slug == "iranair",
        )
    ).scalar_one_or_none()

    if root_id is None:
        raise ValueError("Default manual category Iranair was not created for this organisation")

    category_id = connection.execute(
        select(ManualCategory.id).where(
            ManualCategory.org_id == target.org_id,
            ManualCategory.parent_id == root_id,
            ManualCategory.slug == "general",
        )
    ).scalar_one_or_none()

    if category_id is None:
        raise ValueError("Default manual category Iranair / General was not created")

    # Assigning on the target before INSERT makes SQLAlchemy include the found
    # category in the same statement that creates the manual.
    target.category_id = category_id
