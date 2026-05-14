import enum


class UserRole(str, enum.Enum):
    pilot = "pilot"
    admin = "admin"
    safety = "safety"
    planning = "planning"
    technical = "technical"
    chief_pilot = "chief_pilot"


class SubmissionStatus(str, enum.Enum):
    pending = "pending"
    submitted = "submitted"
    delivered = "delivered"
    failed = "failed"


class ManualAction(str, enum.Enum):
    view = "view"
    download = "download"
