"""Repository helpers for user lookup and organization-scoped lists."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.user import User
from app.models.user_profile_picture import UserProfilePicture


def get_by_email(db: Session, email: str) -> Optional[User]:
    """Fetch a non-deleted user by email address."""
    return db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    """Fetch a non-deleted user by primary key."""
    return db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()


def list_by_org(db: Session, *, org_id: int) -> list[User]:
    """List non-deleted users in one organization."""
    return (
        db.query(User)
        .filter(User.org_id == org_id, User.deleted_at.is_(None))
        .order_by(User.name.asc(), User.id.asc())
        .all()
    )


def get_by_employee_no(
    db: Session,
    *,
    org_id: int,
    employee_no: str,
    exclude_user_id: Optional[int] = None,
) -> Optional[User]:
    """Fetch an active same-organization user by employee number."""
    query = db.query(User).filter(
        User.org_id == org_id,
        func.lower(func.btrim(User.employee_no)) == employee_no.strip().lower(),
        User.deleted_at.is_(None),
    )
    if exclude_user_id is not None:
        query = query.filter(User.id != exclude_user_id)
    return query.first()


def list_by_org_and_roles(db: Session, *, org_id: int, roles: list[UserRole]) -> list[User]:
    """List non-deleted users in an org whose role is one of the requested roles."""
    return (
        db.query(User)
        .filter(
            User.org_id == org_id,
            User.role.in_(roles),
            User.deleted_at.is_(None),
        )
        .order_by(User.name.asc())
        .all()
    )


def list_by_ids(db: Session, *, org_id: int, user_ids: list[int]) -> list[User]:
    """List selected non-deleted users, restricted to a single organization."""
    return (
        db.query(User)
        .filter(
            User.org_id == org_id,
            User.id.in_(user_ids),
            User.deleted_at.is_(None),
        )
        .order_by(User.name.asc())
        .all()
    )


def soft_delete(db: Session, user: User) -> None:
    """Deactivate a user while preserving historical references."""
    user.deleted_at = datetime.now(timezone.utc)
    db.flush()


def create_profile_picture(
    db: Session,
    *,
    org_id: int,
    user_id: int,
    storage_path: str,
    original_filename: str,
    mime_type: str,
    file_size: int,
    sha256: str,
    encrypted_key: str,
    key_nonce: str,
    content_nonce: str,
    encryption_key_id: str,
    encryption_alg: str,
) -> UserProfilePicture:
    """Create encrypted profile picture metadata."""
    picture = UserProfilePicture(
        org_id=org_id,
        user_id=user_id,
        storage_path=storage_path,
        original_filename=original_filename,
        mime_type=mime_type,
        file_size=file_size,
        sha256=sha256,
        encrypted_key=encrypted_key,
        key_nonce=key_nonce,
        content_nonce=content_nonce,
        encryption_key_id=encryption_key_id,
        encryption_alg=encryption_alg,
    )
    db.add(picture)
    db.flush()
    return picture


def get_profile_picture(
    db: Session,
    *,
    org_id: int,
    picture_id: int,
) -> Optional[UserProfilePicture]:
    """Fetch profile picture metadata inside an organization."""
    return (
        db.query(UserProfilePicture)
        .filter(UserProfilePicture.org_id == org_id, UserProfilePicture.id == picture_id)
        .first()
    )
