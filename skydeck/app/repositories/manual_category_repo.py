"""Repository queries for organization-scoped manual category trees.

The API can ask for roots, direct children, the full active tree, or a
root-to-node breadcrumb. SQL query construction stays here so route handlers
work with domain objects instead of repeating tenant and active-state filters.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session as DbSession, selectinload

from app.models.manual_category import ManualCategory


def get_by_id(db: DbSession, category_id: int) -> Optional[ManualCategory]:
    """Fetch an active category by primary key."""
    return (
        db.query(ManualCategory)
        .filter(ManualCategory.id == category_id, ManualCategory.is_active.is_(True))
        .first()
    )


def get_for_org(db: DbSession, *, org_id: int, category_id: int) -> Optional[ManualCategory]:
    """Fetch an active category and enforce organization ownership."""
    return (
        db.query(ManualCategory)
        .filter(
            ManualCategory.id == category_id,
            ManualCategory.org_id == org_id,
            ManualCategory.is_active.is_(True),
        )
        .first()
    )


def list_roots(db: DbSession, *, org_id: int) -> list[ManualCategory]:
    """Return the top-level active categories for an organization."""
    return (
        db.query(ManualCategory)
        .filter(
            ManualCategory.org_id == org_id,
            ManualCategory.parent_id.is_(None),
            ManualCategory.is_active.is_(True),
        )
        .order_by(ManualCategory.sort_order.asc(), ManualCategory.name.asc())
        .all()
    )


def list_children(db: DbSession, *, org_id: int, parent_id: int) -> list[ManualCategory]:
    """Return active direct child categories under a parent."""
    return (
        db.query(ManualCategory)
        .filter(
            ManualCategory.org_id == org_id,
            ManualCategory.parent_id == parent_id,
            ManualCategory.is_active.is_(True),
        )
        .order_by(ManualCategory.sort_order.asc(), ManualCategory.name.asc())
        .all()
    )


def list_all(db: DbSession, *, org_id: int) -> list[ManualCategory]:
    """Return all active categories, preloading children for tree building.

    ``selectinload`` fetches children in a bounded additional query rather than
    issuing one lazy query per category while the recursive response is built.
    """
    return (
        db.query(ManualCategory)
        .options(selectinload(ManualCategory.children))
        .filter(ManualCategory.org_id == org_id, ManualCategory.is_active.is_(True))
        .order_by(ManualCategory.sort_order.asc(), ManualCategory.name.asc())
        .all()
    )


def has_children(db: DbSession, *, category_id: int) -> bool:
    """Check for an active child without loading complete child rows."""
    return (
        db.query(ManualCategory.id)
        .filter(ManualCategory.parent_id == category_id, ManualCategory.is_active.is_(True))
        .first()
        is not None
    )


def get_path(category: ManualCategory) -> list[ManualCategory]:
    """Walk parent links and return a root-first breadcrumb.

    The loop naturally produces leaf-to-root order, so the list is reversed
    once before being serialized for clients.
    """
    path: list[ManualCategory] = []
    current: Optional[ManualCategory] = category
    while current is not None:
        path.append(current)
        current = current.parent
    path.reverse()
    return path
