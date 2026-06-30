"""Idempotent construction of the default manual-category tree.

New organizations receive this navigation structure from a mapper event, while
the auth/signup path can call :func:`ensure_default_categories` to repair older
or partially initialized tenants. Slug paths are stable machine identifiers;
display names may contain spaces or capitalization.
"""

from __future__ import annotations

from sqlalchemy.orm import Session as DbSession

from app.models.enums import AircraftType
from app.models.manual_category import ManualCategory

# Shared declarative seed structure used by both the Org mapper event and the
# repair helper below. List order becomes ``sort_order`` in API navigation.
STANDARD_MANUAL_CATEGORY_CHILDREN: list[tuple[str, str]] = [
    ("Aircraft documents", "aircraft-documents"),
    ("Aircraft Performance", "aircraft-performance"),
    ("Fleet memos", "fleet-memos"),
    ("General", "general"),
    ("MEL CDI", "mel-cdi"),
    ("training documents", "training-documents"),
]

GENERAL_MANUAL_CATEGORY_ROOT = {
    "name": "General",
    "slug": "general",
    "children": STANDARD_MANUAL_CATEGORY_CHILDREN,
}

FLEET_MANUAL_CATEGORY_ROOTS: list[dict] = [
    {
        "name": AircraftType.A330.value,
        "slug": "a330",
        "aircraft_type": AircraftType.A330.value,
        "children": STANDARD_MANUAL_CATEGORY_CHILDREN,
    },
    {
        "name": AircraftType.A300_A600_A310.value,
        "slug": "a300-a600-a310",
        "aircraft_type": AircraftType.A300_A600_A310.value,
        "children": STANDARD_MANUAL_CATEGORY_CHILDREN,
    },
    {
        "name": AircraftType.A320.value,
        "slug": "a320",
        "aircraft_type": AircraftType.A320.value,
        "children": STANDARD_MANUAL_CATEGORY_CHILDREN,
    },
    {
        "name": AircraftType.F100.value,
        "slug": "f100",
        "aircraft_type": AircraftType.F100.value,
        "children": STANDARD_MANUAL_CATEGORY_CHILDREN,
    },
    {
        "name": AircraftType.ATR72_600.value,
        "slug": "atr72-600",
        "aircraft_type": AircraftType.ATR72_600.value,
        "children": STANDARD_MANUAL_CATEGORY_CHILDREN,
    },
]

DEFAULT_MANUAL_CATEGORY_TREE: list[dict] = [
    GENERAL_MANUAL_CATEGORY_ROOT,
    *FLEET_MANUAL_CATEGORY_ROOTS,
]

FLEET_ROOT_SLUG_BY_AIRCRAFT_TYPE = {
    root["aircraft_type"]: root["slug"]
    for root in FLEET_MANUAL_CATEGORY_ROOTS
}
PROTECTED_ROOT_SLUGS = {
    GENERAL_MANUAL_CATEGORY_ROOT["slug"],
    *FLEET_ROOT_SLUG_BY_AIRCRAFT_TYPE.values(),
}


def ensure_default_categories(db: DbSession, *, org_id: int) -> dict[str, ManualCategory]:
    """Create the default manual category tree if missing.

    Returns a mapping keyed by slash-separated slug path, for example:
    ``iranair/general``.
    """
    # Returning created *and* pre-existing rows gives callers a convenient
    # lookup without requiring another query after repair.
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
