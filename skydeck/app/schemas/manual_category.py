from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ManualCategoryPathItem(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class ManualCategoryOut(BaseModel):
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
    id: int
    org_id: int
    parent_id: Optional[int] = None
    name: str
    slug: str
    sort_order: int
    is_active: bool
    children: list[ManualCategoryTreeOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}
