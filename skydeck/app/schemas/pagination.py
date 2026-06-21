"""Reusable page-number pagination request and response models.

Routes validate ``page`` and ``limit`` once, use ``offset`` in SQL queries, and
return the original paging values with a total count and typed item list.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Validated page/limit inputs with a derived SQL offset."""

    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        """Translate a one-based API page into a zero-based SQL row offset."""
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic wrapper for paginated API responses."""

    page: int
    limit: int
    total: int
    items: list[T]
