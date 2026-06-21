"""Pydantic response schemas for manual-library routes.

The API never exposes ``storage_path`` because it is an internal storage key,
not a public URL. Upload/update variants include checksum and status text useful
immediately after mutation, while ``ManualOut`` is the normal listing shape.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.manual_category import ManualCategoryPathItem


class ManualOut(BaseModel):
    """Public metadata for a manual, including its category breadcrumb."""

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
    """Mutation result after file storage and database commit succeed."""

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
    """Mutation result after replacing a PDF and incrementing its version."""

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
    """Minimal confirmation after logical/physical manual deletion."""

    message: str = "Manual deleted successfully"
