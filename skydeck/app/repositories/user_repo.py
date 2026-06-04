"""Repository helpers for user lookup and organization-scoped lists."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.user import User


def get_by_email(db: Session, email: str) -> Optional[User]:
    """Fetch a non-deleted user by email address."""
    return db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    """Fetch a non-deleted user by primary key."""
    return db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()


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
