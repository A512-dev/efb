"""Private online CRUD for user-owned manual PDF annotations."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session as DbSession

from app.core.deps import require_roles
from app.core.errors import AuthorisationError, ConflictError, NotFoundError
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.manual import Manual
from app.models.manual_annotation import ManualAnnotation
from app.models.user import User
from app.repositories import manual_annotation_repo, manual_repo
from app.schemas.auth import ErrorResponse
from app.schemas.manual_annotation import (
    AnnotationPayload,
    ManualAnnotationCollectionOut,
    ManualAnnotationOut,
)
from app.services import audit_service, manual_visibility_service

router = APIRouter(
    prefix="/manuals/{manual_id}/annotations",
    tags=["manual annotations"],
)

_ALL_ROLES = require_roles(
    UserRole.admin,
    UserRole.pilot,
    UserRole.chief_pilot,
    UserRole.safety,
    UserRole.planning,
    UserRole.technical,
)


def _get_current_manual(db: DbSession, *, manual_id: int, user: User) -> Manual:
    manual = manual_repo.get_by_id(db, manual_id)
    if (
        manual is None
        or manual.org_id != user.org_id
        or not manual.is_active
        or not manual_visibility_service.can_access_manual(user, manual)
    ):
        raise NotFoundError("Manual not found")
    return manual


def _ensure_current_version(manual: Manual, version_number: int) -> None:
    if version_number != manual.version_number:
        raise ConflictError(
            f"Manual version {version_number} is archived; current version is "
            f"{manual.version_number}"
        )


def _ensure_payload_owner(payload: AnnotationPayload, user: User) -> None:
    """Reject attempts to assign an annotation to another user."""
    if payload.user_id != user.id:
        raise AuthorisationError("Annotation user_id must match the authenticated user")


def _payload_values(payload: AnnotationPayload) -> dict:
    """Return mutable annotation fields; ownership comes from authentication."""
    return payload.model_dump(mode="python", exclude={"user_id"})


def _annotation_out(annotation: ManualAnnotation) -> ManualAnnotationOut:
    return ManualAnnotationOut(
        id=annotation.id,
        user_id=annotation.user_id,
        manual_id=annotation.manual_id,
        manual_version_number=annotation.manual_version_number,
        annotation_type=annotation.annotation_type,
        page_number=annotation.page_number,
        geometry=annotation.geometry_json,
        style=annotation.style_json,
        selected_text=annotation.selected_text,
        note_text=annotation.note_text,
        created_at=annotation.created_at,
        updated_at=annotation.updated_at,
    )


def _list_out(db: DbSession, *, manual: Manual, user: User) -> list[ManualAnnotationOut]:
    annotations = manual_annotation_repo.list_active(
        db,
        org_id=user.org_id,
        user_id=user.id,
        manual_id=manual.id,
        manual_version_number=manual.version_number,
    )
    return [_annotation_out(annotation) for annotation in annotations]


def _audit_annotation(
    db: DbSession,
    *,
    action: str,
    annotation: ManualAnnotation,
    user: User,
    request: Request,
) -> None:
    audit_service.record(
        db,
        action=action,
        target_type="manual_annotation",
        target_id=annotation.id,
        user_id=user.id,
        org_id=user.org_id,
        ip=request.client.host if request.client else None,
        metadata={
            "manual_id": annotation.manual_id,
            "manual_version_number": annotation.manual_version_number,
            "annotation_type": annotation.annotation_type,
            "annotation_user_id": annotation.user_id,
        },
    )


@router.get(
    "",
    response_model=ManualAnnotationCollectionOut,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="List the current user's annotations for a manual",
)
def list_annotations(
    manual_id: int,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    manual = _get_current_manual(db, manual_id=manual_id, user=current_user)
    return ManualAnnotationCollectionOut(
        user_id=current_user.id,
        manual_id=manual.id,
        manual_version_number=manual.version_number,
        annotations=_list_out(db, manual=manual, user=current_user),
    )


@router.post(
    "",
    response_model=ManualAnnotationOut,
    status_code=201,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Create one annotation for the authenticated user",
)
def create_annotation(
    manual_id: int,
    payload: AnnotationPayload,
    request: Request,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    manual = _get_current_manual(db, manual_id=manual_id, user=current_user)
    _ensure_payload_owner(payload, current_user)
    _ensure_current_version(manual, payload.manual_version_number)

    annotation = manual_annotation_repo.create(
        db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        manual_id=manual.id,
        values=_payload_values(payload),
    )
    _audit_annotation(
        db,
        action="manual.annotation.create",
        annotation=annotation,
        user=current_user,
        request=request,
    )
    db.commit()
    db.refresh(annotation)
    return _annotation_out(annotation)


@router.put(
    "/{annotation_id}",
    response_model=ManualAnnotationOut,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Replace one annotation owned by the authenticated user",
)
def replace_annotation(
    manual_id: int,
    annotation_id: int,
    payload: AnnotationPayload,
    request: Request,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    manual = _get_current_manual(db, manual_id=manual_id, user=current_user)
    _ensure_payload_owner(payload, current_user)
    _ensure_current_version(manual, payload.manual_version_number)

    annotation = manual_annotation_repo.get_owned_by_id(
        db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        manual_id=manual.id,
        annotation_id=annotation_id,
        for_update=True,
    )
    if annotation is None or annotation.deleted_at is not None:
        raise NotFoundError("Annotation not found")
    if annotation.manual_version_number != manual.version_number:
        raise ConflictError("Annotation belongs to an archived manual version")

    annotation = manual_annotation_repo.replace(
        db,
        annotation,
        values=_payload_values(payload),
    )
    _audit_annotation(
        db,
        action="manual.annotation.update",
        annotation=annotation,
        user=current_user,
        request=request,
    )
    db.commit()
    db.refresh(annotation)
    return _annotation_out(annotation)


@router.delete(
    "/{annotation_id}",
    status_code=204,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Delete one annotation owned by the authenticated user",
)
def delete_annotation(
    manual_id: int,
    annotation_id: int,
    request: Request,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    manual = _get_current_manual(db, manual_id=manual_id, user=current_user)
    annotation = manual_annotation_repo.get_owned_by_id(
        db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        manual_id=manual.id,
        annotation_id=annotation_id,
        for_update=True,
    )
    if annotation is None or annotation.deleted_at is not None:
        raise NotFoundError("Annotation not found")
    if annotation.manual_version_number != manual.version_number:
        raise ConflictError("Annotation belongs to an archived manual version")

    annotation = manual_annotation_repo.soft_delete(db, annotation)
    _audit_annotation(
        db,
        action="manual.annotation.delete",
        annotation=annotation,
        user=current_user,
        request=request,
    )
    db.commit()
    return Response(status_code=204)
