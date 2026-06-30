"""HTTP endpoints for browsing and administering manual category navigation.

All manual roles may browse, but only admins may mutate the folder tree. Every
query is scoped to ``current_user.org_id``.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session as DbSession

from app.core.deps import require_roles
from app.core.errors import AppError, ConflictError, NotFoundError
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.manual_category import ManualCategory
from app.models.user import User
from app.repositories import manual_category_repo
from app.schemas.auth import ErrorResponse
from app.schemas.manual_category import (
    ManualCategoryCreate,
    ManualCategoryDeleteOut,
    ManualCategoryMove,
    ManualCategoryOut,
    ManualCategoryPathItem,
    ManualCategoryRename,
    ManualCategoryReorder,
    ManualCategoryTreeOut,
)
from app.services import audit_service, manual_visibility_service

router = APIRouter(prefix="/manual-categories", tags=["manual-categories"])

_ADMIN = require_roles(UserRole.admin)
_ALL_ROLES = require_roles(
    UserRole.admin,
    UserRole.pilot,
    UserRole.chief_pilot,
    UserRole.safety,
    UserRole.planning,
    UserRole.technical,
)


def _client_ip(request: Request) -> str | None:
    """Return caller IP metadata for audit rows."""
    return request.client.host if request.client else None


def _clean_name(name: str) -> str:
    """Normalize a submitted name and reject whitespace-only values."""
    normalized = manual_category_repo.normalize_name(name)
    if not normalized:
        raise AppError("Manual category name is required", code=400)
    return normalized


def _require_category(db: DbSession, *, org_id: int, category_id: int) -> ManualCategory:
    """Fetch one active category in the current tenant."""
    category = manual_category_repo.get_for_org(db, org_id=org_id, category_id=category_id)
    if category is None:
        raise NotFoundError("Manual category not found")
    return category


def _path_items(category: ManualCategory) -> list[ManualCategoryPathItem]:
    """Convert ORM category ancestors into the compact breadcrumb schema."""
    return [
        ManualCategoryPathItem(id=item.id, name=item.name, slug=item.slug)
        for item in manual_category_repo.get_path(category)
    ]


def _category_out(db: DbSession, category: ManualCategory) -> ManualCategoryOut:
    """Build a flat response with computed breadcrumb and child-presence data."""
    has_children = manual_category_repo.has_children(db, category_id=category.id)
    return ManualCategoryOut(
        id=category.id,
        org_id=category.org_id,
        parent_id=category.parent_id,
        name=category.name,
        slug=category.slug,
        sort_order=category.sort_order,
        is_active=category.is_active,
        has_children=has_children,
        is_leaf=not has_children,
        path=_path_items(category),
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _tree_node(category: ManualCategory) -> ManualCategoryTreeOut:
    """Recursively convert a preloaded ORM subtree into a sorted API tree.

    Inactive children are omitted even if they remain present in the loaded ORM
    relationship for historical reasons.
    """
    active_children = [child for child in category.children if child.is_active]
    active_children.sort(key=lambda item: (item.sort_order, item.name.lower()))
    has_children = len(active_children) > 0
    return ManualCategoryTreeOut(
        id=category.id,
        org_id=category.org_id,
        parent_id=category.parent_id,
        name=category.name,
        slug=category.slug,
        sort_order=category.sort_order,
        is_active=category.is_active,
        has_children=has_children,
        is_leaf=not has_children,
        children=[_tree_node(child) for child in active_children],
    )


def _ensure_no_active_sibling_conflict(
    db: DbSession,
    *,
    org_id: int,
    parent_id: int | None,
    name: str,
    slug: str | None = None,
    exclude_id: int | None = None,
) -> None:
    """Reject duplicate active folder names/slugs under one parent."""
    if manual_category_repo.active_sibling_name_exists(
        db,
        org_id=org_id,
        parent_id=parent_id,
        name=name,
        exclude_id=exclude_id,
    ):
        raise ConflictError("A manual category with this name already exists in this folder")

    if slug is not None and manual_category_repo.active_sibling_slug_exists(
        db,
        org_id=org_id,
        parent_id=parent_id,
        slug=slug,
        exclude_id=exclude_id,
    ):
        raise ConflictError("A manual category with this slug already exists in this folder")


def _ensure_parent_can_accept_children(
    db: DbSession,
    *,
    org_id: int,
    parent_id: int | None,
) -> None:
    """Preserve leaf-only manual storage by not nesting under manual-bearing nodes."""
    if parent_id is None:
        return
    _require_category(db, org_id=org_id, category_id=parent_id)
    if manual_category_repo.has_active_manuals(db, org_id=org_id, category_id=parent_id):
        raise ConflictError("Cannot add a child category under a category that contains manuals")


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
    categories = manual_visibility_service.filter_categories(current_user, categories)
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
    roots = manual_visibility_service.filter_categories(current_user, roots)
    return [_tree_node(root) for root in roots]


@router.post(
    "",
    response_model=ManualCategoryOut,
    status_code=201,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Create a manual category (admin only)",
)
def create_category(
    payload: ManualCategoryCreate,
    request: Request,
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    """Create a root category or a child folder under an existing category."""
    name = _clean_name(payload.name)
    parent_id = payload.parent_id
    _ensure_parent_can_accept_children(db, org_id=current_user.org_id, parent_id=parent_id)

    slug = manual_category_repo.slugify_name(name)
    _ensure_no_active_sibling_conflict(
        db,
        org_id=current_user.org_id,
        parent_id=parent_id,
        name=name,
        slug=slug,
    )

    category = manual_category_repo.create(
        db,
        org_id=current_user.org_id,
        parent_id=parent_id,
        name=name,
        slug=slug,
    )
    audit_service.record(
        db,
        action="manual_category.create",
        target_type="manual_category",
        target_id=category.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=_client_ip(request),
        metadata={"name": category.name, "parent_id": category.parent_id, "slug": category.slug},
    )
    db.commit()
    category = _require_category(db, org_id=current_user.org_id, category_id=category.id)
    return _category_out(db, category)


@router.patch(
    "/reorder",
    response_model=list[ManualCategoryOut],
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Reorder sibling manual categories (admin only)",
)
def reorder_categories(
    payload: ManualCategoryReorder,
    request: Request,
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    """Persist the order of all active categories under one parent/root."""
    parent_id = payload.parent_id
    if parent_id is not None:
        _require_category(db, org_id=current_user.org_id, category_id=parent_id)

    submitted_ids = payload.category_ids
    if len(set(submitted_ids)) != len(submitted_ids):
        raise AppError("Category reorder list contains duplicate IDs", code=400)

    expected_ids = manual_category_repo.list_sibling_ids(
        db,
        org_id=current_user.org_id,
        parent_id=parent_id,
    )
    if set(submitted_ids) != set(expected_ids):
        raise AppError(
            "Category reorder list must contain every active sibling exactly once",
            code=400,
        )

    manual_category_repo.reorder(db, org_id=current_user.org_id, category_ids=submitted_ids)
    audit_service.record(
        db,
        action="manual_category.reorder",
        target_type="manual_category_order",
        target_id=parent_id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=_client_ip(request),
        metadata={"parent_id": parent_id, "category_ids": submitted_ids},
    )
    db.commit()
    categories = manual_category_repo.list_siblings(
        db,
        org_id=current_user.org_id,
        parent_id=parent_id,
    )
    return [_category_out(db, category) for category in categories]


@router.patch(
    "/{category_id}",
    response_model=ManualCategoryOut,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Rename a manual category (admin only)",
)
def rename_category(
    category_id: int,
    payload: ManualCategoryRename,
    request: Request,
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    """Rename a category without changing its stable slug/path identity."""
    category = _require_category(db, org_id=current_user.org_id, category_id=category_id)
    name = _clean_name(payload.name)
    _ensure_no_active_sibling_conflict(
        db,
        org_id=current_user.org_id,
        parent_id=category.parent_id,
        name=name,
        exclude_id=category.id,
    )

    old_name = category.name
    category = manual_category_repo.rename(db, category, name=name)
    audit_service.record(
        db,
        action="manual_category.rename",
        target_type="manual_category",
        target_id=category.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=_client_ip(request),
        metadata={"old_name": old_name, "new_name": category.name},
    )
    db.commit()
    category = _require_category(db, org_id=current_user.org_id, category_id=category.id)
    return _category_out(db, category)


@router.patch(
    "/{category_id}/move",
    response_model=ManualCategoryOut,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Move a manual category (admin only)",
)
def move_category(
    category_id: int,
    payload: ManualCategoryMove,
    request: Request,
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    """Move a category under another parent or back to the root level."""
    category = _require_category(db, org_id=current_user.org_id, category_id=category_id)
    new_parent_id = payload.parent_id
    _ensure_parent_can_accept_children(db, org_id=current_user.org_id, parent_id=new_parent_id)

    if manual_category_repo.is_self_or_descendant(
        db,
        org_id=current_user.org_id,
        category_id=category.id,
        possible_parent_id=new_parent_id,
    ):
        raise AppError("Cannot move a category inside itself", code=400)

    _ensure_no_active_sibling_conflict(
        db,
        org_id=current_user.org_id,
        parent_id=new_parent_id,
        name=category.name,
        slug=category.slug,
        exclude_id=category.id,
    )

    old_parent_id = category.parent_id
    category = manual_category_repo.move(db, category, parent_id=new_parent_id)
    audit_service.record(
        db,
        action="manual_category.move",
        target_type="manual_category",
        target_id=category.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=_client_ip(request),
        metadata={"old_parent_id": old_parent_id, "new_parent_id": new_parent_id},
    )
    db.commit()
    category = _require_category(db, org_id=current_user.org_id, category_id=category.id)
    return _category_out(db, category)


@router.delete(
    "/{category_id}",
    response_model=ManualCategoryDeleteOut,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Delete a manual category subtree (admin only)",
)
def delete_category(
    category_id: int,
    request: Request,
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    """Soft-delete an empty category subtree after ensuring no manuals remain."""
    category = _require_category(db, org_id=current_user.org_id, category_id=category_id)
    if manual_category_repo.subtree_contains_manuals(
        db,
        org_id=current_user.org_id,
        category_id=category.id,
    ):
        raise ConflictError("Cannot delete a category that contains manuals")

    path = [item.name for item in manual_category_repo.get_path(category)]
    affected_count = manual_category_repo.soft_delete_subtree(
        db,
        org_id=current_user.org_id,
        category_id=category.id,
    )
    audit_service.record(
        db,
        action="manual_category.delete",
        target_type="manual_category",
        target_id=category.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=_client_ip(request),
        metadata={"path": " / ".join(path), "affected_count": affected_count},
    )
    db.commit()
    return ManualCategoryDeleteOut()


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
    """List direct children after confirming the parent belongs to the tenant.

    Returning 404 for absent and out-of-organization IDs avoids leaking the
    existence of another tenant's category.
    """
    category = _require_category(db, org_id=current_user.org_id, category_id=category_id)
    if not manual_visibility_service.can_access_category(current_user, category):
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
    category = _require_category(db, org_id=current_user.org_id, category_id=category_id)
    if not manual_visibility_service.can_access_category(current_user, category):
        raise NotFoundError("Manual category not found")
    return _path_items(category)
