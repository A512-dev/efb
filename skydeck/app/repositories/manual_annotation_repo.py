"""Persistence operations for user-owned manual annotations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session as DbSession

from app.models.manual_annotation import ManualAnnotation


def list_active(
    db: DbSession,
    *,
    org_id: int,
    user_id: int,
    manual_id: int,
    manual_version_number: int,
) -> list[ManualAnnotation]:
    """Return the user's active annotations for one exact PDF version."""
    return (
        db.query(ManualAnnotation)
        .filter(
            ManualAnnotation.org_id == org_id,
            ManualAnnotation.user_id == user_id,
            ManualAnnotation.manual_id == manual_id,
            ManualAnnotation.manual_version_number == manual_version_number,
            ManualAnnotation.deleted_at.is_(None),
        )
        .order_by(ManualAnnotation.page_number, ManualAnnotation.id)
        .all()
    )


def get_owned_by_id(
    db: DbSession,
    *,
    org_id: int,
    user_id: int,
    manual_id: int,
    annotation_id: int,
    for_update: bool = False,
) -> Optional[ManualAnnotation]:
    """Fetch an annotation without exposing another user's row."""
    query = db.query(ManualAnnotation).filter(
        ManualAnnotation.id == annotation_id,
        ManualAnnotation.org_id == org_id,
        ManualAnnotation.user_id == user_id,
        ManualAnnotation.manual_id == manual_id,
    )
    if for_update:
        query = query.with_for_update()
    return query.first()


def create(
    db: DbSession,
    *,
    org_id: int,
    user_id: int,
    manual_id: int,
    values: dict,
) -> ManualAnnotation:
    """Create an annotation from already validated API values."""
    annotation = ManualAnnotation(
        org_id=org_id,
        user_id=user_id,
        manual_id=manual_id,
        manual_version_number=values["manual_version_number"],
        annotation_type=values["annotation_type"],
        page_number=values["page_number"],
        geometry_json=values["geometry"],
        style_json=values["style"],
        selected_text=values.get("selected_text"),
        note_text=values.get("note_text"),
    )
    db.add(annotation)
    db.flush()
    return annotation


def replace(
    db: DbSession,
    annotation: ManualAnnotation,
    *,
    values: dict,
) -> ManualAnnotation:
    """Replace mutable annotation content."""
    annotation.manual_version_number = values["manual_version_number"]
    annotation.annotation_type = values["annotation_type"]
    annotation.page_number = values["page_number"]
    annotation.geometry_json = values["geometry"]
    annotation.style_json = values["style"]
    annotation.selected_text = values.get("selected_text")
    annotation.note_text = values.get("note_text")
    annotation.updated_at = datetime.now(timezone.utc)
    annotation.deleted_at = None
    db.flush()
    return annotation


def soft_delete(db: DbSession, annotation: ManualAnnotation) -> ManualAnnotation:
    """Soft-delete an annotation while retaining audit/history linkage."""
    now = datetime.now(timezone.utc)
    annotation.deleted_at = now
    annotation.updated_at = now
    db.flush()
    return annotation
