"""Centralized best-effort audit-logging helper.

Every security-relevant action (upload, delete, download, submit, login)
must flow through here so the audit_logs table is the single source of
truth for compliance investigations.

The caller supplies the transaction's existing SQLAlchemy session. A flush
makes the row part of that transaction, while the caller retains authority to
commit or roll back the business action and its audit evidence together.
"""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session as DbSession

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def record(
    db: DbSession,
    *,
    action: str,
    target_type: str,
    target_id: Optional[str] = None,
    user_id: Optional[int] = None,
    org_id: Optional[int] = None,
    ip: Optional[str] = None,
    device_info: Optional[dict] = None,
    metadata: Optional[dict] = None,
) -> None:
    """Append an audit row without failing the user-facing operation.

    This deliberately catches database/serialization errors because audit
    telemetry should not turn a successful core action into a 500 response.
    The exception is still logged for operators. Note that SQLAlchemy may mark
    a transaction failed after a flush error, so callers should still follow
    normal rollback handling around their overall workflow.
    """
    try:
        # Audit failures should not break the user action that triggered them.
        db.add(
            AuditLog(
                org_id=org_id,
                user_id=user_id,
                action=action,
                target_type=target_type,
                target_id=str(target_id) if target_id is not None else None,
                ip=ip,
                device_info_json=device_info,
                metadata_json=metadata,
            )
        )
        db.flush()
    except Exception:
        logger.exception("Failed to write audit log: action=%s target=%s", action, target_type)
