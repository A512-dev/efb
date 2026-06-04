"""Pydantic response schemas for manual library routes."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.manual_category import ManualCategoryPathItem


class ManualOut(BaseModel):
    """Public representation of a manual record."""

    id: int
    org_id: int
    category_id: int
    category_path: list[ManualCategoryPathItem] = Field(default_factory=list)
    category_path_text: str
    title: str
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    version_number: int
    is_active: bool
    uploaded_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ManualUploadOut(BaseModel):
    """Response after a successful upload."""

    id: int
    category_id: int
    category_path: list[ManualCategoryPathItem] = Field(default_factory=list)
    category_path_text: str
    title: str
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    sha256: Optional[str] = None
    version_number: int = 1
    message: str = "Manual uploaded successfully"


class ManualUpdateOut(BaseModel):
    """Response after replacing the PDF for an existing manual."""

    id: int
    category_id: int
    category_path: list[ManualCategoryPathItem] = Field(default_factory=list)
    category_path_text: str
    title: str
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    sha256: Optional[str] = None
    version_number: int
    message: str = "Manual updated successfully"


class ManualDeleteOut(BaseModel):
    """Response after a manual has been deleted."""

    message: str = "Manual deleted successfully"
