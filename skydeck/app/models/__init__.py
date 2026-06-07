"""Import all models so Alembic and SQLAlchemy metadata can discover them."""

from app.models.audit_log import AuditLog
from app.models.enums import ManualAction, SubmissionStatus, UserRole
from app.models.form_template import FormTemplate
from app.models.form_version import FormVersion
from app.models.login_attempt import LoginAttempt
from app.models.manual import Manual
from app.models.manual_access_log import ManualAccessLog
from app.models.manual_category import ManualCategory
from app.models.manual_update_event import ManualUpdateEvent
from app.models.manual_update_read import ManualUpdateRead
from app.models.message import Message
from app.models.message_attachment import MessageAttachment
from app.models.org import Org
from app.models.session import Session
from app.models.submission import Submission
from app.models.submission_attachment import SubmissionAttachment
from app.models.user import User

__all__ = [
    "AuditLog",
    "FormTemplate",
    "FormVersion",
    "LoginAttempt",
    "Manual",
    "ManualAccessLog",
    "ManualAction",
    "ManualCategory",
    "ManualUpdateEvent",
    "ManualUpdateRead",
    "Message",
    "MessageAttachment",
    "Org",
    "Session",
    "Submission",
    "SubmissionAttachment",
    "SubmissionStatus",
    "User",
    "UserRole",
]
