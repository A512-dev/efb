"""Private annotation CRUD and offline reconciliation for manual PDFs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session as DbSession

from app.core.deps import require_roles
from app.core.errors import ConflictError, NotFoundError
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.manual import Manual
from app.models.manual_annotation import ManualAnnotation
from app.models.user import User
from app.repositories import manual_annotation_repo, manual_repo
from app.schemas.auth import ErrorResponse
from app.schemas.manual_annotation import (
    AnnotationAppliedOut,
    AnnotationConflictOut,
    AnnotationDeleteChange,
    AnnotationPayload,
    AnnotationUpsertChange,
    ManualAnnotationCollectionOut,
    ManualAnnotationOut,
    ManualAnnotationReplace,
    ManualAnnotationSyncOut,
    ManualAnnotationSyncRequest,
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


def _payload_values(payload: AnnotationPayload) -> dict:
    return payload.model_dump(mode="python")


def _annotation_out(annotation: ManualAnnotation) -> ManualAnnotationOut:
    return ManualAnnotationOut(
        id=annotation.id,
        client_id=annotation.client_id,
        manual_id=annotation.manual_id,
        manual_version_number=annotation.manual_version_number,
        annotation_type=annotation.annotation_type,
        page_number=annotation.page_number,
        geometry=annotation.geometry_json,
        style=annotation.style_json,
        selected_text=annotation.selected_text,
        note_text=annotation.note_text,
        revision=annotation.revision,
        created_at=annotation.created_at,
        updated_at=annotation.updated_at,
    )


def _matches_payload(annotation: ManualAnnotation, values: dict) -> bool:
    return (
        annotation.client_id == values["client_id"]
        and annotation.manual_version_number == values["manual_version_number"]
        and annotation.annotation_type == values["annotation_type"]
        and annotation.page_number == values["page_number"]
        and annotation.geometry_json == values["geometry"]
        and annotation.style_json == values["style"]
        and annotation.selected_text == values.get("selected_text")
        and annotation.note_text == values.get("note_text")
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
            "revision": annotation.revision,
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
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Create one annotation",
)
def create_annotation(
    manual_id: int,
    payload: AnnotationPayload,
    request: Request,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    manual = _get_current_manual(db, manual_id=manual_id, user=current_user)
    _ensure_current_version(manual, payload.manual_version_number)
    values = _payload_values(payload)

    existing = manual_annotation_repo.get_owned_by_client_id(
        db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        manual_id=manual.id,
        client_id=payload.client_id,
        for_update=True,
    )
    if existing is not None:
        if existing.deleted_at is None and _matches_payload(existing, values):
            return _annotation_out(existing)
        raise ConflictError("client_id is already used by a different annotation state")

    annotation = manual_annotation_repo.create(
        db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        manual_id=manual.id,
        values=values,
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


@router.post(
    "/sync",
    response_model=ManualAnnotationSyncOut,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Reconcile queued annotation changes",
)
def sync_annotations(
    manual_id: int,
    payload: ManualAnnotationSyncRequest,
    request: Request,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    manual = _get_current_manual(db, manual_id=manual_id, user=current_user)
    _ensure_current_version(manual, payload.manual_version_number)

    applied: list[AnnotationAppliedOut] = []
    conflicts: list[AnnotationConflictOut] = []
    for change in payload.changes:
        if change.operation == "upsert":
            _sync_upsert(
                db,
                manual=manual,
                user=current_user,
                change=change,
                applied=applied,
                conflicts=conflicts,
            )
        else:
            _sync_delete(
                db,
                manual=manual,
                user=current_user,
                change=change,
                applied=applied,
                conflicts=conflicts,
            )

    audit_service.record(
        db,
        action="manual.annotations.sync",
        target_type="manual",
        target_id=manual.id,
        user_id=current_user.id,
        org_id=current_user.org_id,
        ip=request.client.host if request.client else None,
        metadata={
            "manual_version_number": manual.version_number,
            "change_count": len(payload.changes),
            "applied_count": len(applied),
            "conflict_count": len(conflicts),
        },
    )
    db.commit()
    return ManualAnnotationSyncOut(
        manual_id=manual.id,
        manual_version_number=manual.version_number,
        annotations=_list_out(db, manual=manual, user=current_user),
        applied=applied,
        conflicts=conflicts,
    )


def _sync_upsert(
    db: DbSession,
    *,
    manual: Manual,
    user: User,
    change: AnnotationUpsertChange,
    applied: list[AnnotationAppliedOut],
    conflicts: list[AnnotationConflictOut],
) -> None:
    values = _payload_values(change.annotation)
    if change.annotation.manual_version_number != manual.version_number:
        conflicts.append(
            _conflict(change, reason="manual_version_mismatch", annotation=None)
        )
        return

    annotation = manual_annotation_repo.get_owned_by_client_id(
        db,
        org_id=user.org_id,
        user_id=user.id,
        manual_id=manual.id,
        client_id=change.annotation.client_id,
        for_update=True,
    )
    if annotation is None:
        if change.expected_revision != 0:
            conflicts.append(_conflict(change, reason="annotation_missing", annotation=None))
            return
        annotation = manual_annotation_repo.create(
            db,
            org_id=user.org_id,
            user_id=user.id,
            manual_id=manual.id,
            values=values,
        )
    elif annotation.deleted_at is not None:
        conflicts.append(_conflict(change, reason="annotation_deleted", annotation=annotation))
        return
    elif annotation.manual_version_number != manual.version_number:
        conflicts.append(_conflict(change, reason="annotation_archived", annotation=annotation))
        return
    elif change.expected_revision == 0 and _matches_payload(annotation, values):
        pass
    elif annotation.revision != change.expected_revision:
        conflicts.append(_conflict(change, reason="revision_mismatch", annotation=annotation))
        return
    else:
        annotation = manual_annotation_repo.replace(db, annotation, values=values)

    applied.append(
        AnnotationAppliedOut(
            operation="upsert",
            client_id=annotation.client_id,
            revision=annotation.revision,
        )
    )


def _sync_delete(
    db: DbSession,
    *,
    manual: Manual,
    user: User,
    change: AnnotationDeleteChange,
    applied: list[AnnotationAppliedOut],
    conflicts: list[AnnotationConflictOut],
) -> None:
    annotation = manual_annotation_repo.get_owned_by_client_id(
        db,
        org_id=user.org_id,
        user_id=user.id,
        manual_id=manual.id,
        client_id=change.client_id,
        for_update=True,
    )
    if annotation is None:
        conflicts.append(_conflict(change, reason="annotation_missing", annotation=None))
        return
    if annotation.manual_version_number != manual.version_number:
        conflicts.append(_conflict(change, reason="annotation_archived", annotation=annotation))
        return
    if annotation.deleted_at is not None:
        if annotation.revision == change.expected_revision + 1:
            applied.append(
                AnnotationAppliedOut(
                    operation="delete",
                    client_id=annotation.client_id,
                    revision=annotation.revision,
                )
            )
            return
        conflicts.append(_conflict(change, reason="annotation_deleted", annotation=annotation))
        return
    if annotation.revision != change.expected_revision:
        conflicts.append(_conflict(change, reason="revision_mismatch", annotation=annotation))
        return

    annotation = manual_annotation_repo.soft_delete(db, annotation)
    applied.append(
        AnnotationAppliedOut(
            operation="delete",
            client_id=annotation.client_id,
            revision=annotation.revision,
        )
    )


def _conflict(
    change: AnnotationUpsertChange | AnnotationDeleteChange,
    *,
    reason: str,
    annotation: ManualAnnotation | None,
) -> AnnotationConflictOut:
    client_id: UUID = (
        change.annotation.client_id if change.operation == "upsert" else change.client_id
    )
    return AnnotationConflictOut(
        operation=change.operation,
        client_id=client_id,
        reason=reason,
        server_revision=annotation.revision if annotation is not None else None,
        server_deleted=annotation.deleted_at is not None if annotation is not None else False,
        server_annotation=(
            _annotation_out(annotation)
            if annotation is not None and annotation.deleted_at is None
            else None
        ),
    )


@router.put(
    "/{annotation_id}",
    response_model=ManualAnnotationOut,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
    summary="Replace one annotation",
)
def replace_annotation(
    manual_id: int,
    annotation_id: int,
    payload: ManualAnnotationReplace,
    request: Request,
    current_user: User = Depends(_ALL_ROLES),
    db: DbSession = Depends(get_db),
):
    manual = _get_current_manual(db, manual_id=manual_id, user=current_user)
    _ensure_current_version(manual, payload.annotation.manual_version_number)
    annotation = manual_annotation_repo.get_owned_by_id(
        db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        manual_id=manual.id,
        annotation_id=annotation_id,
        for_update=True,
    )
    if annotation is None:
        raise NotFoundError("Annotation not found")
    if annotation.deleted_at is not None:
        raise ConflictError("Annotation was deleted")
    if annotation.manual_version_number != manual.version_number:
        raise ConflictError("Annotation belongs to an archived manual version")
    if annotation.client_id != payload.annotation.client_id:
        raise ConflictError("client_id cannot be changed")
    if annotation.revision != payload.expected_revision:
        raise ConflictError(f"Revision conflict; current revision is {annotation.revision}")

    annotation = manual_annotation_repo.replace(
        db,
        annotation,
        values=_payload_values(payload.annotation),
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
    summary="Delete one annotation",
)
def delete_annotation(
    manual_id: int,
    annotation_id: int,
    request: Request,
    expected_revision: int = Query(..., ge=1),
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
    if annotation is None:
        raise NotFoundError("Annotation not found")
    if annotation.deleted_at is not None:
        raise ConflictError("Annotation was already deleted")
    if annotation.manual_version_number != manual.version_number:
        raise ConflictError("Annotation belongs to an archived manual version")
    if annotation.revision != expected_revision:
        raise ConflictError(f"Revision conflict; current revision is {annotation.revision}")

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
