"""Shared SQLAlchemy declarative base.

Every ORM model inherits from :class:`Base`. That gives Alembic one metadata
registry containing the full schema and lets relationships resolve across
separate model modules.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models.

    The class intentionally has no custom behavior; it is a common registry
    and typing anchor for SQLAlchemy's declarative mapping system.
    """

    pass
