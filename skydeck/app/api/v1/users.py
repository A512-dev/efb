"""User profile, encrypted picture, and administrator user-management routes.

Ordinary users can read/update their own profile and view pictures belonging to
same-organization users. Administrators additionally list and soft-delete
accounts. Passwords, roles, and tenant ownership are not editable here.
"""

from __future__ import annotations

import hashlib
import io
import secrets

from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from app.core.deps import get_current_user, require_roles
from app.core.errors import ConflictError, NotFoundError, StorageError
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories import user_repo
from app.schemas.auth import ErrorResponse
from app.schemas.user import (
    AdminUserProfileUpdateRequest,
    UserDeleteResponse,
    UserListItemResponse,
    UserMeResponse,
    UserProfileUpdateRequest,
)
from app.services import audit_service
from app.services.attachment_crypto import decrypt_profile_picture, encrypt_profile_picture
from app.services.profile_picture_service import read_and_validate_profile_picture
from app.services.storage import get_profile_picture_storage

router = APIRouter(prefix="/users", tags=["users"])
_ADMIN = require_roles(UserRole.admin)


@router.get(
    "",
    response_model=list[UserListItemResponse],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
    summary="List users in the current admin's organization",
)
def list_users(
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    """Return only active users inside the authenticated admin's tenant."""
    return [
        UserListItemResponse.model_validate(user)
        for user in user_repo.list_by_org(db, org_id=current_user.org_id)
    ]


@router.get(
    "/me",
    response_model=UserMeResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Current authenticated user profile",
)
def me(current_user: User = Depends(get_current_user)):
    """Serialize the already-authenticated ORM user into the safe public shape."""
    return UserMeResponse.model_validate(current_user)


@router.patch(
    "/me/profile",
    response_model=UserMeResponse,
    responses={
        401: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Update current user's profile fields",
)
def update_my_profile(
    body: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Apply only supplied editable fields and audit actual changes.

    Pydantic has already normalized text/date inputs. The explicit employee
    number lookup gives a friendly conflict, while the database constraint and
    ``IntegrityError`` handler close the race between concurrent updates.
    """
    updates = body.model_dump(exclude_unset=True)

    if "employee_no" in updates:
        existing_user = user_repo.get_by_employee_no(
            db,
            org_id=current_user.org_id,
            employee_no=updates["employee_no"],
            exclude_user_id=current_user.id,
        )
        if existing_user is not None:
            raise ConflictError("Employee ID is taken.")

    # Avoid an empty commit/audit event when the submitted values equal current
    # values.
    changed_fields = []
    for field, value in updates.items():
        if getattr(current_user, field) != value:
            setattr(current_user, field, value)
            changed_fields.append(field)

    if changed_fields:
        audit_service.record(
            db,
            action="user.profile.update",
            target_type="user",
            target_id=current_user.id,
            user_id=current_user.id,
            org_id=current_user.org_id,
            metadata={"fields": sorted(changed_fields)},
        )
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ConflictError("Employee ID is taken.") from exc
        db.refresh(current_user)

    return UserMeResponse.model_validate(current_user)

@router.patch(
    "/{user_id}/admin-profile",
    response_model=UserListItemResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Admin update of a user's position and aircraft type",
)
def update_user_designation(
    user_id: int,
    body: AdminUserProfileUpdateRequest,
    request: Request,
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    """Allow administrators to set or change the position and aircraft type of a user."""
    target_user = user_repo.get_by_id(db, user_id)
    if target_user is None or target_user.org_id != current_user.org_id:
        raise NotFoundError("User not found")

    updates = body.model_dump(exclude_unset=True)
    changed_fields = []

    if "position" in updates and updates["position"] != target_user.position:
        target_user.position = updates["position"]
        changed_fields.append("position")
    aircraft_type = updates["aircraft_type"].value if "aircraft_type" in updates else None
    if aircraft_type is not None and aircraft_type != target_user.aircraft_type:
        target_user.aircraft_type = aircraft_type
        changed_fields.append("aircraft_type")

    if changed_fields:
        audit_service.record(
            db,
            action="user.admin_update",
            target_type="user",
            target_id=target_user.id,
            user_id=current_user.id,
            org_id=current_user.org_id,
            ip=request.client.host if request.client else None,
            metadata={
                "fields": sorted(changed_fields),
                "target_email": target_user.email,
            },
        )
        db.commit()
        db.refresh(target_user)

    return UserListItemResponse.model_validate(target_user)


@router.post(
    "/me/profile-picture",
    response_model=UserMeResponse,
    responses={
        401: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
    },
    summary="Upload current user's encrypted profile picture",
)
def upload_my_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Atomically replace the current picture metadata with encrypted storage.

    The new ciphertext is saved first. If SQL work fails it is deleted; after a
    successful commit the old ciphertext is removed. This ordering ensures the
    committed profile never points at a file deleted too early.
    """
    picture = read_and_validate_profile_picture(file)
    encrypted = encrypt_profile_picture(picture.contents)
    storage = get_profile_picture_storage()
    old_picture = (
        user_repo.get_profile_picture(
            db,
            org_id=current_user.org_id,
            picture_id=current_user.profile_picture_id,
        )
        if current_user.profile_picture_id is not None
        else None
    )

    # Track external side effects for compensation if the DB transaction fails.
    saved_path: str | None = None
    old_storage_path = old_picture.storage_path if old_picture is not None else None
    try:
        relative_path = f"{current_user.id}/{secrets.token_hex(8)}_{picture.filename}.enc"
        saved_path = storage.save(relative_path, encrypted.ciphertext)
        stored_picture = user_repo.create_profile_picture(
            db,
            org_id=current_user.org_id,
            user_id=current_user.id,
            storage_path=saved_path,
            original_filename=picture.filename,
            mime_type=picture.mime_type,
            file_size=picture.size,
            sha256=picture.sha256,
            encrypted_key=encrypted.encrypted_key,
            key_nonce=encrypted.key_nonce,
            content_nonce=encrypted.content_nonce,
            encryption_key_id=encrypted.key_id,
            encryption_alg=encrypted.alg,
        )
        current_user.profile_picture_id = stored_picture.id
        if old_picture is not None:
            db.delete(old_picture)

        audit_service.record(
            db,
            action="user.profile_picture.upload",
            target_type="user",
            target_id=current_user.id,
            user_id=current_user.id,
            org_id=current_user.org_id,
            metadata={"profile_picture_id": stored_picture.id, "filename": picture.filename},
        )
        db.commit()
    except Exception:
        db.rollback()
        if saved_path is not None:
            storage.delete(saved_path)
        raise

    # Old bytes are no longer referenced after commit, so cleanup is now safe.
    if old_storage_path is not None:
        storage.delete(old_storage_path)

    db.refresh(current_user)
    return UserMeResponse.model_validate(current_user)


@router.get(
    "/me/profile-picture",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Download current user's profile picture",
)
def download_my_profile_picture(
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Download the current user's decrypted profile picture."""
    return _download_profile_picture(current_user.id, current_user=current_user, db=db)


@router.get(
    "/{user_id}/profile-picture",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Download a user's profile picture",
)
def download_profile_picture(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Download another same-organization user's decrypted profile picture."""
    return _download_profile_picture(user_id, current_user=current_user, db=db)


@router.delete(
    "/{user_id}",
    response_model=UserDeleteResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Delete a user in the current admin's organization",
)
def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(_ADMIN),
    db: DbSession = Depends(get_db),
):
    """Soft-delete a same-tenant user while preventing admin self-deletion."""
    if user_id == current_user.id:
        raise ConflictError("Admins cannot delete their own account")

    target_user = user_repo.get_by_id(db, user_id)
    if target_user is None or target_user.org_id != current_user.org_id:
        raise NotFoundError("User not found")

    user_repo.soft_delete(db, target_user)
    audit_service.record(
        db,
        action="user.delete",
        target_type="user",
        target_id=target_user.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=request.client.host if request.client else None,
        metadata={"email": target_user.email, "role": target_user.role.value},
    )
    db.commit()
    return UserDeleteResponse()


def _download_profile_picture(
    user_id: int,
    *,
    current_user: User,
    db: DbSession,
) -> StreamingResponse:
    """Authorize, decrypt, verify, audit, and stream one profile picture.

    The target user lookup enforces tenant visibility before picture metadata or
    storage existence is revealed. ``inline`` disposition lets browsers render
    the image while still supplying its original filename.
    """
    target_user = user_repo.get_by_id(db, user_id)
    if target_user is None or target_user.org_id != current_user.org_id:
        raise NotFoundError("User not found")
    if target_user.profile_picture_id is None:
        raise NotFoundError("Profile picture not found")

    picture = user_repo.get_profile_picture(
        db,
        org_id=current_user.org_id,
        picture_id=target_user.profile_picture_id,
    )
    if picture is None or picture.user_id != target_user.id:
        raise NotFoundError("Profile picture not found")

    storage = get_profile_picture_storage()
    if not storage.exists(picture.storage_path):
        raise NotFoundError("Profile picture file missing from storage")

    # Plaintext is produced only in memory after both user and storage
    # authorization checks succeed.
    plaintext = decrypt_profile_picture(
        ciphertext=storage.read(picture.storage_path),
        encrypted_key=picture.encrypted_key,
        key_nonce=picture.key_nonce,
        content_nonce=picture.content_nonce,
    )
    if hashlib.sha256(plaintext).hexdigest() != picture.sha256:
        raise StorageError("Profile picture integrity check failed")

    audit_service.record(
        db,
        action="user.profile_picture.download",
        target_type="user_profile_picture",
        target_id=picture.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        metadata={"profile_user_id": target_user.id},
    )
    db.commit()

    return StreamingResponse(
        io.BytesIO(plaintext),
        media_type=picture.mime_type,
        headers={"Content-Disposition": f'inline; filename="{picture.original_filename}"'},
    )
