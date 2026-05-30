from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class FormFieldOut(BaseModel):
    name: str
    type: str
    required: bool = False
    options: Optional[list[str]] = None
    items: Optional[list[str]] = None
    multiple: Optional[bool] = None


class ActiveFormOut(BaseModel):
    form_id: int
    template_name: str
    version: int
    fields: list[dict[str, Any]]
    created_at: datetime
