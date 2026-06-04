"""SQLAlchemy model for immutable versions of form schemas."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.form_template import FormTemplate
    from app.models.submission import Submission


class FormVersion(Base):
    """A numbered snapshot of a form template's JSON schema."""

    __tablename__ = "form_versions"
    __table_args__ = (
        UniqueConstraint("template_id", "version_number", name="uq_form_versions_template_version"),
        CheckConstraint("version_number >= 1", name="ck_form_versions_version_number"),
        Index("idx_form_versions_template_id", "template_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    template_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("form_templates.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    # schema_json is intentionally flexible because form fields are dynamic.
    schema_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # ── relationships ──────────────────────────────────────
    template: Mapped[FormTemplate] = relationship(back_populates="versions")
    submissions: Mapped[list[Submission]] = relationship(back_populates="form_version")
