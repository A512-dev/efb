"""Repository queries for organization-scoped manual category trees.

The API can ask for roots, direct children, the full active tree, or a
root-to-node breadcrumb. SQL query construction stays here so route handlers
work with domain objects instead of repeating tenant and active-state filters.
"""

from __future__ import annotations

import re
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import selectinload

from app.models.manual import Manual
from app.models.manual_category import ManualCategory


def normalize_name(name: str) -> str:
    """Trim and collapse user-entered folder names."""
    return " ".join(name.strip().split())


def slugify_name(name: str) -> str:
    """Create a stable sibling-unique machine identifier from a display name."""
    slug = re.sub(r"[^\w]+", "-", normalize_name(name).lower()).strip("-_")
    return slug or "category"


def _parent_filter(parent_id: Optional[int]):
    """Return the SQLAlchemy condition for one sibling group."""
    if parent_id is None:
        return ManualCategory.parent_id.is_(None)
    return ManualCategory.parent_id == parent_id


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


def list_siblings(db: DbSession, *, org_id: int, parent_id: Optional[int]) -> list[ManualCategory]:
    """Return active direct categories under one parent or root."""
    return (
        db.query(ManualCategory)
        .filter(
            ManualCategory.org_id == org_id,
            _parent_filter(parent_id),
            ManualCategory.is_active.is_(True),
        )
        .order_by(ManualCategory.sort_order.asc(), ManualCategory.name.asc())
        .all()
    )


def list_sibling_ids(db: DbSession, *, org_id: int, parent_id: Optional[int]) -> list[int]:
    """Return active direct category IDs for reorder validation."""
    return [category.id for category in list_siblings(db, org_id=org_id, parent_id=parent_id)]


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


def has_active_manuals(db: DbSession, *, org_id: int, category_id: int) -> bool:
    """Check whether active manuals live directly in one category."""
    return (
        db.query(Manual.id)
        .filter(
            Manual.org_id == org_id,
            Manual.category_id == category_id,
            Manual.deleted_at.is_(None),
            Manual.is_active.is_(True),
        )
        .first()
        is not None
    )


def _subtree_ids_select(*, org_id: int, category_id: int):
    """Build a recursive CTE selecting an active category subtree."""
    descendants = (
        select(ManualCategory.id)
        .where(
            ManualCategory.id == category_id,
            ManualCategory.org_id == org_id,
            ManualCategory.is_active.is_(True),
        )
        .cte(name="manual_category_subtree", recursive=True)
    )
    descendants = descendants.union_all(
        select(ManualCategory.id).where(
            ManualCategory.parent_id == descendants.c.id,
            ManualCategory.org_id == org_id,
            ManualCategory.is_active.is_(True),
        )
    )
    return select(descendants.c.id)


def list_subtree_ids(db: DbSession, *, org_id: int, category_id: int) -> list[int]:
    """Return active IDs from category through descendants."""
    return list(db.execute(_subtree_ids_select(org_id=org_id, category_id=category_id)).scalars())


def subtree_contains_manuals(db: DbSession, *, org_id: int, category_id: int) -> bool:
    """Check for any non-deleted manual inside a category subtree."""
    subtree_ids = list_subtree_ids(db, org_id=org_id, category_id=category_id)
    if not subtree_ids:
        return False

    return (
        db.query(Manual.id)
        .filter(
            Manual.org_id == org_id,
            Manual.category_id.in_(subtree_ids),
            Manual.deleted_at.is_(None),
        )
        .first()
        is not None
    )


def is_self_or_descendant(
    db: DbSession,
    *,
    org_id: int,
    category_id: int,
    possible_parent_id: Optional[int],
) -> bool:
    """Return true when a move would place a category inside itself."""
    if possible_parent_id is None:
        return False
    if possible_parent_id == category_id:
        return True

    return (
        db.query(ManualCategory.id)
        .filter(
            ManualCategory.id == possible_parent_id,
            ManualCategory.id.in_(
                _subtree_ids_select(org_id=org_id, category_id=category_id)
            ),
        )
        .first()
        is not None
    )


def active_sibling_name_exists(
    db: DbSession,
    *,
    org_id: int,
    parent_id: Optional[int],
    name: str,
    exclude_id: Optional[int] = None,
) -> bool:
    """Check case-insensitive display-name uniqueness inside one folder."""
    query = db.query(ManualCategory.id).filter(
        ManualCategory.org_id == org_id,
        _parent_filter(parent_id),
        ManualCategory.is_active.is_(True),
        func.lower(ManualCategory.name) == normalize_name(name).lower(),
    )
    if exclude_id is not None:
        query = query.filter(ManualCategory.id != exclude_id)
    return query.first() is not None


def active_sibling_slug_exists(
    db: DbSession,
    *,
    org_id: int,
    parent_id: Optional[int],
    slug: str,
    exclude_id: Optional[int] = None,
) -> bool:
    """Check database slug uniqueness inside one active sibling group."""
    query = db.query(ManualCategory.id).filter(
        ManualCategory.org_id == org_id,
        _parent_filter(parent_id),
        ManualCategory.is_active.is_(True),
        ManualCategory.slug == slug,
    )
    if exclude_id is not None:
        query = query.filter(ManualCategory.id != exclude_id)
    return query.first() is not None


def next_sort_order(db: DbSession, *, org_id: int, parent_id: Optional[int]) -> int:
    """Return the next append position for one sibling group."""
    current_max = (
        db.query(func.coalesce(func.max(ManualCategory.sort_order), 0))
        .filter(
            ManualCategory.org_id == org_id,
            _parent_filter(parent_id),
            ManualCategory.is_active.is_(True),
        )
        .scalar()
    )
    return int(current_max or 0) + 1


def create(
    db: DbSession,
    *,
    org_id: int,
    parent_id: Optional[int],
    name: str,
    slug: str,
) -> ManualCategory:
    """Create a category at the end of one sibling group."""
    category = ManualCategory(
        org_id=org_id,
        parent_id=parent_id,
        name=normalize_name(name),
        slug=slug,
        sort_order=next_sort_order(db, org_id=org_id, parent_id=parent_id),
    )
    db.add(category)
    db.flush()
    return category


def rename(db: DbSession, category: ManualCategory, *, name: str) -> ManualCategory:
    """Change only the human-readable category name."""
    category.name = normalize_name(name)
    db.flush()
    return category


def move(
    db: DbSession,
    category: ManualCategory,
    *,
    parent_id: Optional[int],
) -> ManualCategory:
    """Move a category to the end of another sibling group."""
    category.parent_id = parent_id
    category.sort_order = next_sort_order(db, org_id=category.org_id, parent_id=parent_id)
    db.flush()
    return category


def reorder(db: DbSession, *, org_id: int, category_ids: list[int]) -> None:
    """Persist direct sibling order using the supplied ID sequence."""
    categories = (
        db.query(ManualCategory)
        .filter(
            ManualCategory.org_id == org_id,
            ManualCategory.id.in_(category_ids),
            ManualCategory.is_active.is_(True),
        )
        .all()
    )
    by_id = {category.id: category for category in categories}
    for sort_order, category_id in enumerate(category_ids, start=1):
        by_id[category_id].sort_order = sort_order
    db.flush()


def soft_delete_subtree(db: DbSession, *, org_id: int, category_id: int) -> int:
    """Hide an active category subtree and return affected row count."""
    subtree_ids = list_subtree_ids(db, org_id=org_id, category_id=category_id)
    if not subtree_ids:
        return 0

    return (
        db.query(ManualCategory)
        .filter(
            ManualCategory.org_id == org_id,
            ManualCategory.id.in_(subtree_ids),
            ManualCategory.is_active.is_(True),
        )
        .update(
            {
                ManualCategory.is_active: False,
                ManualCategory.updated_at: func.now(),
            },
            synchronize_session=False,
        )
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
