from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session as DbSession, selectinload

from app.models.manual_category import ManualCategory


def get_by_id(db: DbSession, category_id: int) -> Optional[ManualCategory]:
    return (
        db.query(ManualCategory)
        .filter(ManualCategory.id == category_id, ManualCategory.is_active.is_(True))
        .first()
    )


def get_for_org(db: DbSession, *, org_id: int, category_id: int) -> Optional[ManualCategory]:
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
    return (
        db.query(ManualCategory)
        .options(selectinload(ManualCategory.children))
        .filter(ManualCategory.org_id == org_id, ManualCategory.is_active.is_(True))
        .order_by(ManualCategory.sort_order.asc(), ManualCategory.name.asc())
        .all()
    )


def has_children(db: DbSession, *, category_id: int) -> bool:
    return (
        db.query(ManualCategory.id)
        .filter(ManualCategory.parent_id == category_id, ManualCategory.is_active.is_(True))
        .first()
        is not None
    )


def get_path(category: ManualCategory) -> list[ManualCategory]:
    path: list[ManualCategory] = []
    current: Optional[ManualCategory] = category
    while current is not None:
        path.append(current)
        current = current.parent
    path.reverse()
    return path
