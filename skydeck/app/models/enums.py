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


class SubmissionStatus(str, enum.Enum):
    """Lifecycle states for submitted forms."""

    pending = "pending"
    submitted = "submitted"
    delivered = "delivered"
    failed = "failed"


class ManualAction(str, enum.Enum):
    """Audit actions that can be recorded for manual access."""

    view = "view"
    download = "download"
