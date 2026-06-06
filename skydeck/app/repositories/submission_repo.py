"""Repository helpers for form submissions."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import joinedload

from app.models.submission import Submission


def create(db: DbSession, *, submission: Submission) -> Submission:
    """Persist an already-constructed submission and return it with an id."""
    db.add(submission)
    db.flush()
    return submission


def list_by_org(
    db: DbSession,
    *,
    org_id: int,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[Submission], int]:
    """Return a paginated submission list and total count for an organization."""
    query = db.query(Submission).filter(Submission.org_id == org_id)
    total = query.count()
    items = query.order_by(Submission.created_at.desc()).offset(offset).limit(limit).all()
    return items, total


def get_by_id(db: DbSession, submission_id: int) -> Optional[Submission]:
    """Fetch a submission with attachments loaded for detail views."""
    return (
        db.query(Submission)
        .options(joinedload(Submission.attachments))
        .filter(Submission.id == submission_id)
        .first()
    )
