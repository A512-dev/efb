"""Pydantic schemas for manual read tracking."""

from datetime import datetime

from pydantic import BaseModel


class ManualReadOut(BaseModel):
    id: int
    org_id: int
    user_id: int
    manual_id: int
    read_at: datetime
    last_read_at: datetime
    read_count: int
    created_at: datetime
    user_name: str
    manual_title: str
