"""Pydantic schemas for manual-read tracking responses.

The response combines persisted counters/timestamps with denormalized user and
manual display names assembled by the API layer.
"""

from datetime import datetime

from pydantic import BaseModel


class ManualReadOut(BaseModel):
    """One user's accumulated read state for one manual."""

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
