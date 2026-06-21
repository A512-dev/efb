"""Internal role-constrained messaging and encrypted attachment downloads.

Messages are tenant-scoped and intentionally asymmetric:

* pilots/chief pilots send to every administrator automatically;
* administrators choose one or more pilot/chief-pilot recipients;
* other roles cannot send with the current business rules.

One logical send creates one ``Message`` row per recipient so read receipts are
independent. Attachment bytes are validated, encrypted, and stored separately
for every resulting message row.
"""

from __future__ import annotations

import io
import json
import secrets

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DbSession

from app.core.deps import get_current_user
from app.core.errors import AppError, AuthorisationError, NotFoundError, StorageError
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.message import Message
from app.models.user import User
from app.repositories import message_repo, user_repo
from app.schemas.auth import ErrorResponse
from app.schemas.message import (
    MessageCreateRequest,
    MessageCreateResponse,
    MessageOut,
    MessageReadResponse,
    MessageRecipientOut,
)
from app.schemas.pagination import PaginatedResponse
from app.services import audit_service
from app.services.attachment_crypto import decrypt_attachment, encrypt_attachment
from app.services.message_attachment_service import (
    ValidatedAttachment,
    read_and_validate_attachments,
)
from app.services.storage import get_message_attachment_storage

router = APIRouter(prefix="/messages", tags=["messages"])

# Keeping these policy sets near the router makes current product rules visible
# without burying them inside generic repository queries.
_ADMIN_RECIPIENT_ROLES = {UserRole.admin}
_ADMIN_SENDER_ROLES = {UserRole.admin}
_PILOT_RECIPIENT_ROLES = {UserRole.pilot, UserRole.chief_pilot}


def _normalise_recipient_ids(recipient_ids: list[int] | None) -> list[int]:
    """Return a deduplicated recipient id list while preserving client order."""
    if not recipient_ids:
        return []
    # Preserve order while removing duplicates.
    return list(dict.fromkeys(recipient_ids))


def _get_admin_recipients(db: DbSession, *, org_id: int) -> list[User]:
    """Resolve the automatic admin recipients for pilot-originated messages."""
    return user_repo.list_by_org_and_roles(db, org_id=org_id, roles=list(_ADMIN_RECIPIENT_ROLES))


def _get_users_by_ids(db: DbSession, *, org_id: int, user_ids: list[int]) -> list[User]:
    """Fetch explicitly selected recipients inside the sender's organization."""
    if not user_ids:
        return []
    return user_repo.list_by_ids(db, org_id=org_id, user_ids=user_ids)


def _resolve_recipients(
    db: DbSession,
    *,
    current_user: User,
    recipient_ids: list[int] | None,
) -> list[User]:
    """Resolve recipients and enforce sender-role/tenant policy.

    Explicit IDs are never trusted directly: repository resolution constrains
    them to active users in the sender's organization, and missing IDs produce
    a not-found error before any message rows are created.
    """
    normalised_ids = _normalise_recipient_ids(recipient_ids)

    if current_user.role in {UserRole.pilot, UserRole.chief_pilot}:
        if normalised_ids:
            raise AuthorisationError("Pilots cannot choose message recipients")
        recipients = _get_admin_recipients(db, org_id=current_user.org_id)
        if not recipients:
            raise AppError("No admin recipients are available in this organisation", code=400)
        return recipients

    if current_user.role in _ADMIN_SENDER_ROLES:
        if not normalised_ids:
            raise AppError("Admin messages require at least one recipient_id", code=400)
        recipients = _get_users_by_ids(db, org_id=current_user.org_id, user_ids=normalised_ids)
        found_ids = {recipient.id for recipient in recipients}
        missing_ids = [user_id for user_id in normalised_ids if user_id not in found_ids]
        if missing_ids:
            raise NotFoundError(f"Recipient(s) not found: {missing_ids}")
        invalid = [
            recipient for recipient in recipients if recipient.role not in _PILOT_RECIPIENT_ROLES
        ]
        if invalid:
            raise AuthorisationError("Admins can only send messages to pilot/chief_pilot users")
        return recipients

    raise AuthorisationError("Your role is not permitted to send messages")


def _create_message_rows(
    db: DbSession,
    *,
    current_user: User,
    recipients: list[User],
    subject: str | None,
    body: str,
) -> list[Message]:
    """Create one recipient-specific message row for each resolved user."""
    return [
        message_repo.create(
            db,
            org_id=current_user.org_id,
            sender_id=current_user.id,
            recipient_id=recipient.id,
            subject=subject,
            body=body,
        )
        for recipient in recipients
    ]


def _parse_recipient_ids_form(recipient_ids: str | None) -> list[int] | None:
    """Parse multipart recipient IDs from JSON array or comma-separated text.

    Multipart form fields arrive as strings, unlike the typed JSON endpoint.
    Supporting both formats keeps browser/form clients simple while converging
    on the same list-of-integers policy.
    """
    if recipient_ids is None or not recipient_ids.strip():
        return None

    raw = recipient_ids.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = raw.split(",")

    if not isinstance(parsed, list):
        parsed = [parsed]

    ids: list[int] = []
    for item in parsed:
        try:
            user_id = int(str(item).strip())
        except ValueError:
            raise AppError("recipient_ids must contain only integer ids", code=400) from None
        if user_id > 0:
            ids.append(user_id)
    return ids


def _store_attachments_for_message(
    db: DbSession,
    *,
    message: Message,
    attachments: list[ValidatedAttachment],
    saved_paths: list[str],
) -> None:
    """Encrypt/store attachments and add their metadata to one message.

    ``saved_paths`` is an external-operation undo log. If a later database or
    storage step fails, the caller deletes every path accumulated so far.
    """
    storage = get_message_attachment_storage()
    for attachment in attachments:
        # A fresh data key and random storage key are generated per
        # message/attachment copy.
        encrypted = encrypt_attachment(attachment.contents)
        relative_path = f"{message.id}/{secrets.token_hex(8)}_{attachment.filename}.enc"
        storage_path = storage.save(relative_path, encrypted.ciphertext)
        saved_paths.append(storage_path)
        message_repo.create_attachment(
            db,
            org_id=message.org_id,
            message_id=message.id,
            storage_path=storage_path,
            original_filename=attachment.filename,
            mime_type=attachment.mime_type,
            file_size=attachment.size,
            sha256=attachment.sha256,
            encrypted_key=encrypted.encrypted_key,
            key_nonce=encrypted.key_nonce,
            content_nonce=encrypted.content_nonce,
            encryption_key_id=encrypted.key_id,
            encryption_alg=encrypted.alg,
        )


def _message_response_items(
    db: DbSession,
    *,
    current_user: User,
    messages: list[Message],
) -> list[MessageOut]:
    """Reload newly created messages with relationships for response serialization."""
    items: list[MessageOut] = []
    for message in messages:
        refreshed = message_repo.get_visible_to_user(db, message_id=message.id, user=current_user)
        if refreshed is not None:
            items.append(MessageOut.model_validate(refreshed))
    return items


@router.post(
    "",
    response_model=MessageCreateResponse,
    status_code=201,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
    summary="Send an internal message",
)
def send_message(
    body: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Send a text-only message and audit all recipient-specific rows.

    Rules:
      - pilot/chief_pilot users send to all admins in their organisation.
      - admin users send to explicitly selected pilot/chief_pilot recipients.
    """
    recipients = _resolve_recipients(
        db,
        current_user=current_user,
        recipient_ids=body.recipient_ids,
    )
    created = _create_message_rows(
        db,
        current_user=current_user,
        recipients=recipients,
        subject=body.subject,
        body=body.body,
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

    items = _message_response_items(db, current_user=current_user, messages=created)

    return MessageCreateResponse(items=items)


@router.post(
    "/with-attachments",
    response_model=MessageCreateResponse,
    status_code=201,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
    },
    summary="Send an internal message with encrypted attachments",
)
def send_message_with_attachments(
    body: str = Form(..., min_length=1, max_length=5000),
    subject: str | None = Form(None, max_length=200),
    recipient_ids: str | None = Form(None),
    files: list[UploadFile] | None = File(None),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Send a message and store validated attachments encrypted at rest.

    PostgreSQL rollback cannot remove files already written to disk, so the
    exception path rolls back SQL and walks ``saved_paths`` to compensate.
    """
    recipients = _resolve_recipients(
        db,
        current_user=current_user,
        recipient_ids=_parse_recipient_ids_form(recipient_ids),
    )
    attachments = read_and_validate_attachments(files)
    saved_paths: list[str] = []
    storage = get_message_attachment_storage()

    try:
        created = _create_message_rows(
            db,
            current_user=current_user,
            recipients=recipients,
            subject=subject,
            body=body,
        )
        for message in created:
            _store_attachments_for_message(
                db,
                message=message,
                attachments=attachments,
                saved_paths=saved_paths,
            )

        audit_service.record(
            db,
            action="message.send",
            target_type="message",
            target_id=",".join(str(message.id) for message in created),
            user_id=current_user.id,
            org_id=current_user.org_id,
            metadata={
                "recipient_ids": [recipient.id for recipient in recipients],
                "attachment_count": len(attachments),
            },
        )
        db.commit()
    except Exception:
        # Compensating cleanup approximates an atomic transaction across the
        # database and filesystem.
        db.rollback()
        for path in saved_paths:
            storage.delete(path)
        raise

    return MessageCreateResponse(
        items=_message_response_items(db, current_user=current_user, messages=created)
    )


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
    """List one mailbox view with bounded page-number pagination."""
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


@router.get(
    "/recipients",
    response_model=list[MessageRecipientOut],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
    summary="List admin-selectable pilot message recipients",
)
def list_message_recipients(
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Return same-organization pilots/chief pilots an admin can message."""
    if current_user.role not in _ADMIN_SENDER_ROLES:
        raise AuthorisationError("Only admins can list message recipients")

    recipients = user_repo.list_by_org_and_roles(
        db,
        org_id=current_user.org_id,
        roles=list(_PILOT_RECIPIENT_ROLES),
    )
    return [MessageRecipientOut.model_validate(user) for user in recipients]


@router.post(
    "/{message_id}/read",
    response_model=MessageReadResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Mark a received message as read",
)
def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Set a first-read receipt after confirming the caller is the recipient.

    Senders may view the row but cannot mark it read on behalf of its recipient.
    """
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


@router.get(
    "/{message_id}/attachments/{attachment_id}",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Download a message attachment",
)
def download_message_attachment(
    message_id: int,
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Authorize, decrypt, integrity-check, audit, and stream an attachment.

    Both sender and recipient can download because both can view the parent
    message. Plaintext exists only in memory for the duration of this response.
    """
    message = message_repo.get_visible_to_user(db, message_id=message_id, user=current_user)
    if message is None:
        raise NotFoundError("Message not found")

    attachment = message_repo.get_attachment_for_message(
        db,
        org_id=current_user.org_id,
        message_id=message.id,
        attachment_id=attachment_id,
    )
    if attachment is None:
        raise NotFoundError("Attachment not found")

    storage = get_message_attachment_storage()
    if not storage.exists(attachment.storage_path):
        raise NotFoundError("Attachment file missing from storage")

    plaintext = decrypt_attachment(
        ciphertext=storage.read(attachment.storage_path),
        encrypted_key=attachment.encrypted_key,
        key_nonce=attachment.key_nonce,
        content_nonce=attachment.content_nonce,
    )
    # AES-GCM already authenticates ciphertext; the stored plaintext digest
    # additionally verifies that database metadata matches the decrypted file.
    if attachment.sha256 != _sha256(plaintext):
        raise StorageError("Attachment integrity check failed")

    audit_service.record(
        db,
        action="message.attachment.download",
        target_type="message_attachment",
        target_id=attachment.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        metadata={"message_id": message.id, "filename": attachment.original_filename},
    )
    db.commit()

    filename = attachment.original_filename or f"attachment_{attachment.id}"
    return StreamingResponse(
        io.BytesIO(plaintext),
        media_type=attachment.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _sha256(contents: bytes) -> str:
    """Return a lowercase hexadecimal SHA-256 digest for integrity checks."""
    import hashlib

    return hashlib.sha256(contents).hexdigest()
