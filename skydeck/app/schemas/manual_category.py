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
    children: list[ManualCategoryTreeOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}
