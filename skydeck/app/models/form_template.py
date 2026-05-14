from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.form_version import FormVersion
    from app.models.org import Org


class FormTemplate(Base):
    __tablename__ = "form_templates"
    __table_args__ = (Index("idx_form_templates_org_id", "org_id"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # ── relationships ──────────────────────────────────────
    org: Mapped[Org] = relationship(back_populates="form_templates")
    versions: Mapped[list[FormVersion]] = relationship(
        back_populates="template", cascade="all, delete-orphan"
    )
