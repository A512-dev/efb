"""Shared enum values persisted by SQLAlchemy models and exposed in schemas."""

import enum


class UserRole(str, enum.Enum):
    """Roles used for authorization decisions across the API."""

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
