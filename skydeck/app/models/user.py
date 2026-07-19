"""SQLAlchemy model for authenticated application users.

Users belong to exactly one organization and carry one coarse-grained role.
Passwords are represented only by bcrypt hashes; API serializers deliberately
exclude ``password_hash`` and deletion state.
"""

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
    from app.models.manual_annotation import ManualAnnotation
    from app.models.manual_reads import ManualRead
    from app.models.org import Org
    from app.models.session import Session
    from app.models.user_profile_picture import UserProfilePicture


class User(Base):
    """A person who can authenticate and act within one organization.

    Expiry fields hold operational credentials relevant to aviation staff.
    ``employee_no`` is unique within current business rules, and soft deletion
    keeps historical relationships intact while repository queries hide the
    account from active use.
    """

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

    # a field for later:
    #password_changed_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_constraint=False, native_enum=True),
        nullable=False,
        default= UserRole.pilot,
    )
    employee_no: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[str] = mapped_column(Text, nullable=False)

    aircraft_type: Mapped[str] = mapped_column(Text, nullable=False)
    medical_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    passport_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    license_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    profile_picture_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("user_profile_pictures.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    # Users are soft-deleted so old sessions and audit rows can still reference them.
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── relationships ──────────────────────────────────────
    org: Mapped[Org] = relationship(back_populates="users")
    sessions: Mapped[list[Session]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    uploaded_manuals: Mapped[list[Manual]] = relationship(back_populates="uploaded_by_user")
    manual_reads: Mapped[list[ManualRead]] = relationship(back_populates="user")
    manual_annotations: Mapped[list[ManualAnnotation]] = relationship(back_populates="user")
    profile_picture: Mapped[Optional[UserProfilePicture]] = relationship(
        "UserProfilePicture",
        foreign_keys=[profile_picture_id],
    )

    @property
    def profile_picture_url(self) -> Optional[str]:
        """Return the authenticated download URL for the current picture.

        This is computed rather than stored so route prefixes stay consistent
        and changing a picture ID immediately changes whether a URL is exposed.
        """
        if self.profile_picture_id is None:
            return None
        return f"/api/v1/users/{self.id}/profile-picture"


    @property
    def password(self):
        # Dummy property to satisfy sqladmin's form_columns check
        return None
