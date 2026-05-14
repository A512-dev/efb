from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Identity, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SubmissionStatus

if TYPE_CHECKING:
    from app.models.form_version import FormVersion
    from app.models.org import Org
    from app.models.submission_attachment import SubmissionAttachment
    from app.models.user import User


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        Index("idx_submissions_org_id", "org_id"),
        Index("idx_submissions_user_id", "user_id"),
        Index("idx_submissions_form_version_id", "form_version_id"),
        Index("idx_submissions_created_at", "created_at"),
        Index("idx_submissions_hash_id", "hash_id"),
        Index("idx_submissions_status", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    form_version_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("form_versions.id"), nullable=False
    )
    data_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, name="submission_status", create_constraint=False, native_enum=True),
        server_default="pending",
    )
    hash_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    device_info_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # ── relationships ──────────────────────────────────────
    org: Mapped[Org] = relationship(back_populates="submissions")
    user: Mapped[User] = relationship(back_populates="submissions")
    form_version: Mapped[FormVersion] = relationship(back_populates="submissions")
    attachments: Mapped[list[SubmissionAttachment]] = relationship(
        back_populates="submission", cascade="all, delete-orphan"
    )
