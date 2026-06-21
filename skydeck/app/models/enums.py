"""Shared enum values persisted by SQLAlchemy and exposed by the API.

Subclassing ``str`` makes enum members serialize naturally in JSON while still
giving Python code a closed, typo-resistant set of values. Changing persisted
values requires a database migration because PostgreSQL stores native enums.
"""

import enum


class UserRole(str, enum.Enum):
    """Roles used for authorization decisions across the API.

    Route dependencies compare these members directly, and SQLAlchemy maps them
    to PostgreSQL's ``user_role`` enum.
    """

    pilot = "pilot"
    admin = "admin"
    safety = "safety"
    planning = "planning"
    technical = "technical"
    chief_pilot = "chief_pilot"


class ManualAction(str, enum.Enum):
    """Audit actions that can be recorded for manual access."""

    view = "view"
    download = "download"
