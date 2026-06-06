"""Manual category browsing routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.deps import require_roles
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.manual_category import ManualCategory
from app.models.user import User
from app.repositories import manual_category_repo
from app.schemas.auth import ErrorResponse
from app.schemas.manual_category import ManualCategoryOut, ManualCategoryPathItem, ManualCategoryTreeOut

router = APIRouter(prefix="/manual-categories", tags=["manual-categories"])

_ALL_ROLES = require_roles(
    UserRole.admin,
    UserRole.pilot,
    UserRole.chief_pilot,
    UserRole.safety,
    UserRole.planning,
    UserRole.technical,
)


def _path_items(category: ManualCategory) -> list[ManualCategoryPathItem]:
    """Convert ORM category ancestors into the compact breadcrumb schema."""
    return [
        ManualCategoryPathItem(id=item.id, name=item.name, slug=item.slug)
        for item in manual_category_repo.get_path(category)
    ]


def _category_out(db: DbSession, category: ManualCategory) -> ManualCategoryOut:
    """Build the public category response with path and has_children metadata."""
    return ManualCategoryOut(
        id=category.id,
        org_id=category.org_id,
        parent_id=category.parent_id,
        name=category.name,
        slug=category.slug,
        sort_order=category.sort_order,
        is_active=category.is_active,
        has_children=manual_category_repo.has_children(db, category_id=category.id),
        path=_path_items(category),
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _tree_node(category: ManualCategory) -> ManualCategoryTreeOut:
    """Recursively convert an ORM category subtree into an API tree node."""
    active_children = [child for child in category.children if child.is_active]
    active_children.sort(key=lambda item: (item.sort_order, item.name.lower()))
    return ManualCategoryTreeOut(
        id=category.id,
        org_id=category.org_id,
        parent_id=category.parent_id,
        name=category.name,
        slug=category.slug,
        sort_order=category.sort_order,
        is_active=category.is_active,
        children=[_tree_node(child) for child in active_children],
    )


@router.get(
    "/roots",
    response_model=list[ManualCategoryOut],
    responses={401: {"model": ErrorResponse}},
    summary="List root manual categories",
)
def list_root_categories(
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    """List root categories available to the caller's organization."""
    categories = manual_category_repo.list_roots(db, org_id=current_user.org_id)
    return [_category_out(db, category) for category in categories]


@router.get(
    "/tree",
    response_model=list[ManualCategoryTreeOut],
    responses={401: {"model": ErrorResponse}},
    summary="Return the full manual category tree",
)
def get_category_tree(
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    """Return the full active category tree for navigation screens."""
    roots = manual_category_repo.list_roots(db, org_id=current_user.org_id)
    return [_tree_node(root) for root in roots]


@router.get(
    "/{category_id}/children",
    response_model=list[ManualCategoryOut],
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="List direct child categories",
)
def list_category_children(
    category_id: int,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    """List active direct children after checking parent ownership."""
    parent = manual_category_repo.get_for_org(
        db,
        org_id=current_user.org_id,
        category_id=category_id,
    )
    if parent is None:
        raise NotFoundError("Manual category not found")

    children = manual_category_repo.list_children(
        db,
        org_id=current_user.org_id,
        parent_id=category_id,
    )
    return [_category_out(db, category) for category in children]


@router.get(
    "/{category_id}/path",
    response_model=list[ManualCategoryPathItem],
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Return a category breadcrumb path",
)
def get_category_path(
    category_id: int,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    """Return the breadcrumb path from root to a category."""
    category = manual_category_repo.get_for_org(
        db,
        org_id=current_user.org_id,
        category_id=category_id,
    )
    if category is None:
        raise NotFoundError("Manual category not found")
    return _path_items(category)
