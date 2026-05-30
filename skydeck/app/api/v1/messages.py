from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.deps import get_current_user
from app.core.errors import AppError, AuthorisationError, NotFoundError
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories import message_repo, user_repo
from app.schemas.auth import ErrorResponse
from app.schemas.message import MessageCreateRequest, MessageCreateResponse, MessageOut, MessageReadResponse
from app.schemas.pagination import PaginatedResponse
from app.services import audit_service

router = APIRouter(prefix="/messages", tags=["messages"])

_ADMIN_RECIPIENT_ROLES = {UserRole.admin}
_ADMIN_SENDER_ROLES = {UserRole.admin}
_PILOT_RECIPIENT_ROLES = {UserRole.pilot, UserRole.chief_pilot}


def _normalise_recipient_ids(recipient_ids: list[int] | None) -> list[int]:
    if not recipient_ids:
        return []
    # Preserve order while removing duplicates.
    return list(dict.fromkeys(recipient_ids))


def _get_admin_recipients(db: DbSession, *, org_id: int) -> list[User]:
    return user_repo.list_by_org_and_roles(db, org_id=org_id, roles=list(_ADMIN_RECIPIENT_ROLES))


def _get_users_by_ids(db: DbSession, *, org_id: int, user_ids: list[int]) -> list[User]:
    if not user_ids:
        return []
    return user_repo.list_by_ids(db, org_id=org_id, user_ids=user_ids)


@router.post(
    "",
    response_model=MessageCreateResponse,
    status_code=201,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
    summary="Send an internal message",
)
def send_message(
    body: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Send a message.

    Rules:
      - pilot/chief_pilot users send to all admins in their organisation.
      - admin users send to explicitly selected pilot/chief_pilot recipients.
    """
    recipient_ids = _normalise_recipient_ids(body.recipient_ids)

    if current_user.role in {UserRole.pilot, UserRole.chief_pilot}:
        if recipient_ids:
            raise AuthorisationError("Pilots cannot choose message recipients")
        recipients = _get_admin_recipients(db, org_id=current_user.org_id)
        if not recipients:
            raise AppError("No admin recipients are available in this organisation", code=400)

    elif current_user.role in _ADMIN_SENDER_ROLES:
        if not recipient_ids:
            raise AppError("Admin messages require at least one recipient_id", code=400)
        recipients = _get_users_by_ids(db, org_id=current_user.org_id, user_ids=recipient_ids)
        found_ids = {recipient.id for recipient in recipients}
        missing_ids = [user_id for user_id in recipient_ids if user_id not in found_ids]
        if missing_ids:
            raise NotFoundError(f"Recipient(s) not found: {missing_ids}")
        invalid = [recipient for recipient in recipients if recipient.role not in _PILOT_RECIPIENT_ROLES]
        if invalid:
            raise AuthorisationError("Admins can only send messages to pilot/chief_pilot users")

    else:
        raise AuthorisationError("Your role is not permitted to send messages")

    created = []
    for recipient in recipients:
        created.append(
            message_repo.create(
                db,
                org_id=current_user.org_id,
                sender_id=current_user.id,
                recipient_id=recipient.id,
                subject=body.subject,
                body=body.body,
            )
        )

    audit_service.record(
        db,
        action="message.send",
        target_type="message",
        target_id=",".join(str(message.id) for message in created),
        user_id=current_user.id,
        org_id=current_user.org_id,
        metadata={"recipient_ids": [recipient.id for recipient in recipients]},
    )
    db.commit()

    for message in created:
        db.refresh(message)

    return MessageCreateResponse(items=[MessageOut.model_validate(message) for message in created])


@router.get(
    "",
    response_model=PaginatedResponse[MessageOut],
    responses={401: {"model": ErrorResponse}},
    summary="List current user's messages",
)
def list_messages(
    box: message_repo.MessageBox = "inbox",
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    offset = (page - 1) * limit
    items, total = message_repo.list_for_user(
        db,
        user=current_user,
        box=box,
        offset=offset,
        limit=limit,
    )

    return PaginatedResponse(
        page=page,
        limit=limit,
        total=total,
        items=[MessageOut.model_validate(message) for message in items],
    )


@router.post(
    "/{message_id}/read",
    response_model=MessageReadResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Mark a received message as read",
)
def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    message = message_repo.get_visible_to_user(db, message_id=message_id, user=current_user)
    if message is None:
        raise NotFoundError("Message not found")
    if message.recipient_id != current_user.id:
        raise AuthorisationError("Only the recipient can mark this message as read")

    message_repo.mark_read(db, message)
    audit_service.record(
        db,
        action="message.read",
        target_type="message",
        target_id=message.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
    )
    db.commit()
    db.refresh(message)
    return MessageReadResponse(item=MessageOut.model_validate(message))
