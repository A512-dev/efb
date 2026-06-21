"""Pydantic request and response schemas.

Schemas describe data crossing the HTTP boundary. They are deliberately
separate from SQLAlchemy models so database-only fields and relationships do
not leak into public API contracts.
"""
