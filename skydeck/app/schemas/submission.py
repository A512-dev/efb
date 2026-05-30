from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class SubmissionCreateRequest(BaseModel):
    form_version_id: int
    data: dict[str, Any] = Field(..., description="Form field responses as JSON")


class SubmissionOut(BaseModel):
    id: int
    org_id: int
    user_id: int
    user_name: Optional[str] = None
    form_version_id: int
    data_json: dict[str, Any]
    status: str
    hash_id: str
    submitted_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmissionCreateOut(BaseModel):
    submission_id: int
    hash_id: str
    status: str


class AttachmentOut(BaseModel):
    id: int
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    attachment_type: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmissionDetailOut(SubmissionOut):
    ip: Optional[str] = None
    device_info_json: Optional[dict] = None
    attachments: list[AttachmentOut] = []
