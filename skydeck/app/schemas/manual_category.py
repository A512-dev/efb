"""Pydantic schemas for category-tree and breadcrumb responses.

The same category data appears in three useful shapes: a small path segment, a
flat node with computed metadata, and a recursive tree node for navigation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ManualCategoryPathItem(BaseModel):
    """Single ordered segment in a root-to-leaf breadcrumb."""

    id: int
    name: str
    slug: str

    # Permit direct validation from a SQLAlchemy ManualCategory instance.
    model_config = {"from_attributes": True}


class ManualCategoryOut(BaseModel):
    """Flat category response with path and child-presence hints."""

    id: int
    org_id: int
    parent_id: Optional[int] = None
    name: str
    slug: str
    sort_order: int
    is_active: bool
    has_children: bool = False
    is_leaf: bool = True
    path: list[ManualCategoryPathItem] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None


class ManualCategoryTreeOut(BaseModel):
    """Recursive node whose ``children`` contain the same schema type."""

    id: int
    org_id: int
    parent_id: Optional[int] = None
    name: str
    slug: str
    sort_order: int
    is_active: bool
    has_children: bool = False
    is_leaf: bool = True
    children: list[ManualCategoryTreeOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ManualCategoryCreate(BaseModel):
    """Payload for creating a root or child manual category."""

    name: str = Field(..., min_length=1, max_length=200)
    parent_id: Optional[int] = None


class ManualCategoryRename(BaseModel):
    """Payload for changing a category display name."""

    name: str = Field(..., min_length=1, max_length=200)


class ManualCategoryMove(BaseModel):
    """Payload for moving a category under a new parent or to root."""

    parent_id: Optional[int] = None


class ManualCategoryReorder(BaseModel):
    """Ordered direct-sibling IDs for one parent/root level."""

    parent_id: Optional[int] = None
    category_ids: list[int] = Field(..., min_length=1)


class ManualCategoryDeleteOut(BaseModel):
    """Confirmation returned after a category subtree is hidden."""

    message: str = "Manual category deleted successfully"
