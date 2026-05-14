from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ManualOut(BaseModel):
    """Public representation of a manual record."""

    id: int
    org_id: int
    title: str
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    version_number: int
    is_active: bool
    uploaded_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ManualUploadOut(BaseModel):
    """Response after a successful upload."""

    id: int
    title: str
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    sha256: Optional[str] = None
    message: str = "Manual uploaded successfully"

    model_config = {"from_attributes": True}


class ManualDeleteOut(BaseModel):
    message: str = "Manual deleted successfully"
