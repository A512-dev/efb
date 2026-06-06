"""Repository helpers for refresh-token sessions and login attempts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session as DbSession

from app.models.login_attempt import LoginAttempt
from app.models.session import Session


def create_session(
    db: DbSession,
    *,
    user_id: int,
    refresh_token_hash: str,
    expires_at: datetime,
    device_info: Optional[dict] = None,
) -> Session:
    """Create a refresh-token session for a successful login."""
    sess = Session(
        user_id=user_id,
        refresh_token_hash=refresh_token_hash,
        expires_at=expires_at,
        device_info_json=device_info,
    )
    db.add(sess)
    db.flush()
    return sess


def get_by_token_hash(db: DbSession, token_hash: str) -> Optional[Session]:
    """Find a non-revoked session by hashed refresh token."""
    return (
        db.query(Session)
        .filter(
            Session.refresh_token_hash == token_hash,
            Session.revoked_at.is_(None),
        )
        .first()
    )


def revoke_session(db: DbSession, session: Session) -> None:
    """Invalidate a refresh-token session without deleting its audit history."""
    session.revoked_at = datetime.now(timezone.utc)
    db.flush()


def touch_session(db: DbSession, session: Session) -> None:
    """Update the session heartbeat after token refresh or authenticated use."""
    session.last_seen_at = datetime.now(timezone.utc)
    db.flush()


def record_login_attempt(
    db: DbSession,
    *,
    email: str,
    success: bool,
    user_id: Optional[int] = None,
    org_id: Optional[int] = None,
    ip: Optional[str] = None,
    device_info: Optional[dict] = None,
    failure_reason: Optional[str] = None,
) -> None:
    """Store the outcome of a login attempt for audit and security review."""
    db.add(
        LoginAttempt(
            email=email,
            success=success,
            user_id=user_id,
            org_id=org_id,
            ip=ip,
            device_info_json=device_info,
            failure_reason=failure_reason,
        )
    )
    db.flush()
