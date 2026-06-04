"""Repository helpers for reading form templates and versions."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import joinedload

from app.models.form_template import FormTemplate
from app.models.form_version import FormVersion


def get_active_forms(db: DbSession, *, org_id: int) -> list[dict]:
    """Return the latest version of every form template in the org."""
    templates = (
        db.query(FormTemplate)
        .filter(FormTemplate.org_id == org_id)
        .order_by(FormTemplate.created_at.desc())
        .all()
    )
    results = []
    for tpl in templates:
        latest = (
            db.query(FormVersion)
            .filter(FormVersion.template_id == tpl.id)
            .order_by(FormVersion.version_number.desc())
            .first()
        )
        if latest:
            results.append(
                {
                    "form_id": latest.id,
                    "template_name": tpl.name,
                    "version": latest.version_number,
                    "fields": latest.schema_json.get("fields", []),
                    "created_at": latest.created_at,
                }
            )
    return results


def get_version_by_id(db: DbSession, version_id: int) -> Optional[FormVersion]:
    """Fetch a concrete form version with its template relationship loaded."""
    return (
        db.query(FormVersion)
        .options(joinedload(FormVersion.template))
        .filter(FormVersion.id == version_id)
        .first()
    )
