"""FastAPI dependencies for request-scoped auth and RBAC."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session as DbSession

from app.core.errors import AuthenticationError, AuthorisationError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories import user_repo

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: DbSession = Depends(get_db),
) -> User:
    """Extract and validate the Bearer token, return the active ``User``.

    Raises ``AuthenticationError`` (401) if the token is missing,
    malformed, expired, or the user no longer exists.
    """
    if credentials is None:
        raise AuthenticationError("Missing authentication token")

    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired token") from exc

    user_id = int(payload["sub"])
    user = user_repo.get_by_id(db, user_id)

    if user is None:
        raise AuthenticationError("User not found or deactivated")

    return user


def require_roles(*allowed: UserRole) -> Callable[..., User]:
    """Return a dependency that enforces role-based access.

    Usage in a route::

        @router.post("/upload")
        def upload(user: User = Depends(require_roles(UserRole.admin))):
            ...
    """
    allowed_set = set(allowed)

    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_set:
            raise AuthorisationError(
                f"Role '{current_user.role.value}' is not permitted for this action"
            )
        return current_user

    return _check
