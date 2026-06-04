"""Reusable pagination request and response models."""

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
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic wrapper for paginated API responses."""

    page: int
    limit: int
    total: int
    items: list[T]
