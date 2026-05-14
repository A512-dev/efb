from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, Identity, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.form_template import FormTemplate
    from app.models.manual import Manual
    from app.models.submission import Submission
    from app.models.user import User


class Org(Base):
    __tablename__ = "orgs"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    settings_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # ── relationships ──────────────────────────────────────
    users: Mapped[list[User]] = relationship(back_populates="org", cascade="all, delete-orphan")
    manuals: Mapped[list[Manual]] = relationship(back_populates="org", cascade="all, delete-orphan")
    form_templates: Mapped[list[FormTemplate]] = relationship(
        back_populates="org", cascade="all, delete-orphan"
    )
    submissions: Mapped[list[Submission]] = relationship(
        back_populates="org", cascade="all, delete-orphan"
    )
