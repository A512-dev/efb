#skydeck\app\core\deps.py
"""FastAPI dependencies for request-scoped authentication and RBAC.

Routes declare these functions with ``Depends``. FastAPI then runs token
validation before the route body and passes the resulting ORM ``User`` through
the rest of the dependency graph.
"""

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

# ``auto_error=False`` lets the application raise its own AppError and preserve
# the standard {"error", "code"} response envelope for missing credentials.
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
        # JWT verification checks the signature and expiration before returning
        # claims. decode_access_token additionally rejects refresh tokens.
        payload = decode_access_token(credentials.credentials)
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired token") from exc

    # The token stores ``sub`` as a string to follow JWT conventions; database
    # primary keys are integers.
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
    # Convert once when the dependency is configured, not on every request.
    allowed_set = set(allowed)

    def _check(current_user: User = Depends(get_current_user)) -> User:
        """Return the authenticated user only when their role is allowed."""
        # FastAPI calls this inner dependency per request after get_current_user succeeds.
        if current_user.role not in allowed_set:
            raise AuthorisationError(
                f"Role '{current_user.role.value}' is not permitted for this action"
            )
        return current_user

    return _check
