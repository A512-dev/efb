"""Centralised audit-logging helper.

Every security-relevant action (upload, delete, download, submit, login)
must flow through here so the audit_logs table is the single source of
truth for compliance investigations.
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
    """Append an immutable audit row. Never raises — logs and continues."""
    try:
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
