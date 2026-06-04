"""Business logic for authentication, token refresh, and logout.

Every successful login creates a row in the ``sessions`` table.
The raw refresh token is never stored — only its SHA-256 hash.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError
from sqlalchemy.orm import Session as DbSession

from app.core.config import settings
from app.core.errors import AuthenticationError, ConflictError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.enums import UserRole
from app.models.user import User
from app.repositories import session_repo, user_repo
from app.services import audit_service
from app.services.manual_category_service import ensure_default_categories

# Pre-computed bcrypt hash so user-not-found login attempts still
# pay the same CPU cost as real ones (timing-attack mitigation).
_DUMMY_HASH = hash_password("__timing_pad__")

# ── public API ────────────────────────────────────────────────


def signup(
    db: DbSession,
    *,
    name: str,
    email: str,
    password: str,
    ip: Optional[str] = None,
) -> dict:
    """Register a new pilot account.

    MVP rule: new accounts default to ``pilot`` role.
    Raises ``ConflictError`` if the email is already registered.
    """
    if user_repo.get_by_email(db, email):
        raise ConflictError("Email is already registered")

    org = _get_or_create_default_org(db)

    user = User(
        org_id=org.id,
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=UserRole.pilot,
    )
    db.add(user)
    db.flush()

    tokens = _create_session(db, user=user, ip=ip)

    audit_service.record(
        db,
        action="auth.signup",
        target_type="user",
        target_id=user.id,
        user_id=user.id,
        org_id=user.org_id,
        ip=ip,
    )
    db.commit()

    return {
        "user_id": user.id,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
    }


def login(
    db: DbSession,
    *,
    email: str,
    password: str,
    ip: Optional[str] = None,
    device_info: Optional[dict] = None,
) -> dict:
    """Authenticate a user and return token pair + user info."""
    user = user_repo.get_by_email(db, email)

    if user is None:
        verify_password(password, _DUMMY_HASH)
        _record_failure(db, email=email, user=None, ip=ip, device_info=device_info)
        raise AuthenticationError("Invalid email or password")

    if not verify_password(password, user.password_hash):
        _record_failure(db, email=email, user=user, ip=ip, device_info=device_info)
        raise AuthenticationError("Invalid email or password")

    session_repo.record_login_attempt(
        db,
        email=email,
        success=True,
        user_id=user.id,
        org_id=user.org_id,
        ip=ip,
        device_info=device_info,
    )

    tokens = _create_session(db, user=user, ip=ip, device_info=device_info)

    audit_service.record(
        db,
        action="auth.login",
        target_type="user",
        target_id=user.id,
        user_id=user.id,
        org_id=user.org_id,
        ip=ip,
    )
    db.commit()

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "user": {"id": user.id, "name": user.name, "role": user.role.value},
    }


def refresh(db: DbSession, *, raw_refresh_token: str) -> dict:
    """Validate a refresh token and return a new access token."""
    try:
        payload = decode_refresh_token(raw_refresh_token)
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired refresh token") from exc

    token_hash = hash_token(raw_refresh_token)
    sess = session_repo.get_by_token_hash(db, token_hash)

    if sess is None:
        raise AuthenticationError("Session not found or revoked")

    if sess.expires_at.tzinfo is None:
        expires_aware = sess.expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_aware = sess.expires_at

    if expires_aware < datetime.now(timezone.utc):
        raise AuthenticationError("Session expired")

    session_id_from_token = payload.get("sid")
    if session_id_from_token != sess.id:
        raise AuthenticationError("Token / session mismatch")

    user = user_repo.get_by_id(db, sess.user_id)
    if user is None:
        raise AuthenticationError("User no longer exists")

    session_repo.touch_session(db, sess)
    db.commit()

    access_token = create_access_token(user.id, user.role.value)
    return {"access_token": access_token}


def logout(db: DbSession, *, raw_refresh_token: str) -> None:
    """Revoke the session associated with the given refresh token."""
    token_hash = hash_token(raw_refresh_token)
    sess = session_repo.get_by_token_hash(db, token_hash)
    if sess is not None:
        session_repo.revoke_session(db, sess)
        db.commit()


# ── private helpers ───────────────────────────────────────────


def _create_session(
    db: DbSession,
    *,
    user: User,
    ip: Optional[str] = None,
    device_info: Optional[dict] = None,
) -> dict:
    access_token = create_access_token(user.id, user.role.value)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    sess = session_repo.create_session(
        db,
        user_id=user.id,
        refresh_token_hash="pending",
        expires_at=expires_at,
        device_info=device_info,
    )
    refresh_token = create_refresh_token(sess.id)
    sess.refresh_token_hash = hash_token(refresh_token)
    db.flush()

    return {"access_token": access_token, "refresh_token": refresh_token}


def _get_or_create_default_org(db: DbSession):
    from app.models.org import Org

    org = db.query(Org).first()
    if org is None:
        org = Org(name="Default Organisation")
        db.add(org)
        db.flush()

    ensure_default_categories(db, org_id=org.id)
    return org


def _record_failure(
    db: DbSession,
    *,
    email: str,
    user: Optional[User],
    ip: Optional[str],
    device_info: Optional[dict],
) -> None:
    session_repo.record_login_attempt(
        db,
        email=email,
        success=False,
        user_id=user.id if user else None,
        org_id=user.org_id if user else None,
        ip=ip,
        device_info=device_info,
        failure_reason="bad_password" if user else "unknown_email",
    )
    db.commit()
