"""Service helpers for ensuring the default manual category tree exists."""

from __future__ import annotations

from sqlalchemy.orm import Session as DbSession

from app.models.manual_category import ManualCategory


# Shared seed structure used when an organization is created or repaired.
DEFAULT_MANUAL_CATEGORY_TREE: list[dict] = [
    {
        "name": "A300/600",
        "slug": "a300-600",
        "children": [
            ("Aircraft documents", "aircraft-documents"),
            ("Aircraft Performance", "aircraft-performance"),
            ("Fleet memos", "fleet-memos"),
            ("General", "general"),
            ("MEL CDI", "mel-cdi"),
            ("training documents", "training-documents"),
        ],
    },
    {
        "name": "Iranair",
        "slug": "iranair",
        "children": [
            ("Aircraft documents", "aircraft-documents"),
            ("Aircraft Performance", "aircraft-performance"),
            ("Fleet memos", "fleet-memos"),
            ("General", "general"),
            ("MEL CDI", "mel-cdi"),
            ("training documents", "training-documents"),
        ],
    },
    {
        "name": "Training and resources",
        "slug": "training-and-resources",
        "children": [
            ("Aircraft documents", "aircraft-documents"),
            ("Aircraft Performance", "aircraft-performance"),
            ("Fleet memos", "fleet-memos"),
            ("General", "general"),
            ("MEL CDI", "mel-cdi"),
            ("training documents", "training-documents"),
        ],
    },
    {
        "name": "Forms",
        "slug": "forms",
        "children": [
            ("REPORTS", "reports"),
            ("sms", "sms"),
            ("training", "training"),
        ],
    },
    {
        "name": "Safety Issue",
        "slug": "safety-issue",
        "children": [
            ("Aircraft documents", "aircraft-documents"),
            ("Aircraft Performance", "aircraft-performance"),
            ("Fleet memos", "fleet-memos"),
            ("General", "general"),
            ("MEL CDI", "mel-cdi"),
            ("training documents", "training-documents"),
        ],
    },
]


def ensure_default_categories(db: DbSession, *, org_id: int) -> dict[str, ManualCategory]:
    """Create the default manual category tree if missing.

    Returns a mapping keyed by slash-separated slug path, for example:
    ``iranair/general``.
    """
    result: dict[str, ManualCategory] = {}

    for root_order, root_spec in enumerate(DEFAULT_MANUAL_CATEGORY_TREE, start=1):
        # Each lookup is idempotent so this helper can safely run during signup and seeding.
        root = (
            db.query(ManualCategory)
            .filter(
                ManualCategory.org_id == org_id,
                ManualCategory.parent_id.is_(None),
                ManualCategory.slug == root_spec["slug"],
            )
            .first()
        )
        if root is None:
            root = ManualCategory(
                org_id=org_id,
                parent_id=None,
                name=root_spec["name"],
                slug=root_spec["slug"],
                sort_order=root_order,
            )
            db.add(root)
            db.flush()

        result[root.slug] = root

        for child_order, (child_name, child_slug) in enumerate(root_spec["children"], start=1):
            # Children are unique within their parent, not globally across the org.
            child = (
                db.query(ManualCategory)
                .filter(
                    ManualCategory.org_id == org_id,
                    ManualCategory.parent_id == root.id,
                    ManualCategory.slug == child_slug,
                )
                .first()
            )
            if child is None:
                child = ManualCategory(
                    org_id=org_id,
                    parent_id=root.id,
                    name=child_name,
                    slug=child_slug,
                    sort_order=child_order,
                )
                db.add(child)
                db.flush()

            result[f"{root.slug}/{child.slug}"] = child

    return result
