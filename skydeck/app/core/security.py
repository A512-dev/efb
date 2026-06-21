"""JWT token operations and password utilities.

Token types:
    - access: short-lived, carries user_id + role in the payload.
    - refresh: long-lived, carries session_id. Stored as a SHA-256
      hash in the sessions table for revocation lookups.

Raw passwords and refresh tokens must never be persisted. Passwords use
bcrypt's intentionally expensive one-way hashing, while refresh tokens use
SHA-256 because they already contain high-entropy signed data and must be
looked up efficiently.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# Bind configuration once at import time. Changing these settings requires a
# process restart and changing SECRET_KEY invalidates all existing JWTs.
_ALGORITHM = settings.ALGORITHM
_SECRET = settings.SECRET_KEY


# ── JWT helpers ───────────────────────────────────────────────


def create_access_token(
    user_id: int,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create the short-lived JWT sent on authenticated API requests."""
    # JWT timestamps are always UTC-aware to avoid local-time/DST ambiguity.
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": expire,
    }
    # python-jose serializes the datetime ``exp`` claim to a NumericDate.
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def create_refresh_token(session_id: int) -> str:
    """Return an opaque refresh token embedding the session id.

    The token also contains a random ``jti`` (JWT ID) so that
    every refresh token is unique even for the same session.
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload: dict[str, Any] = {
        "sid": session_id,
        "jti": secrets.token_hex(16),
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate an access token. Raises ``JWTError`` on failure."""
    # Decoding verifies both the signature and standard ``exp`` claim.
    payload = jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
    if payload.get("type") != "access":
        raise JWTError("Token type is not 'access'")
    return payload


def decode_refresh_token(token: str) -> dict[str, Any]:
    """Decode and validate a refresh token. Raises ``JWTError`` on failure."""
    payload = jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
    if payload.get("type") != "refresh":
        raise JWTError("Token type is not 'refresh'")
    return payload


# ── password helpers ──────────────────────────────────────────


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt for persistent storage."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


# ── refresh token hashing ────────────────────────────────────


def hash_token(token: str) -> str:
    """Return the deterministic digest stored for a refresh token.

    Determinism allows an incoming raw token to be hashed and matched to its
    session row without retaining the credential itself.
    """
    return hashlib.sha256(token.encode()).hexdigest()
