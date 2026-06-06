"""User profile routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import ErrorResponse
from app.schemas.user import UserMeResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserMeResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Current authenticated user profile",
)
def me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile payload."""
    return UserMeResponse.model_validate(current_user)
