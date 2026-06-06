"""SQLAlchemy model for application users."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Identity, Index, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import CIText
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.manual import Manual
    from app.models.org import Org
    from app.models.session import Session
    from app.models.submission import Submission


class User(Base):
    """A person who can authenticate and act within a single organization."""

    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_org_id", "org_id"),
        Index("idx_users_active", "id", postgresql_where=text("deleted_at IS NULL")),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    org_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    # CIText keeps email lookup case-insensitive at the database layer.
    email: Mapped[str] = mapped_column(CIText(), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_constraint=False, native_enum=True),
        nullable=False,
    )
    employee_no: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[str] = mapped_column(Text, nullable=False)
    aircraft_type: Mapped[str] = mapped_column(Text, nullable=False)
    medical_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    passport_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    license_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    # Users are soft-deleted so old sessions, submissions, and audit rows can still reference them.
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── relationships ──────────────────────────────────────
    org: Mapped[Org] = relationship(back_populates="users")
    sessions: Mapped[list[Session]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    uploaded_manuals: Mapped[list[Manual]] = relationship(back_populates="uploaded_by_user")
    submissions: Mapped[list[Submission]] = relationship(back_populates="user")
