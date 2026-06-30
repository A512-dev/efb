"""Reshape manual categories around fleet roots.

Revision ID: 0014
Revises: 0013
Create Date: 2026-06-30

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0014"
down_revision: Union[str, None] = "0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_STANDARD_CHILDREN = [
    ("Aircraft documents", "aircraft-documents"),
    ("Aircraft Performance", "aircraft-performance"),
    ("Fleet memos", "fleet-memos"),
    ("General", "general"),
    ("MEL CDI", "mel-cdi"),
    ("training documents", "training-documents"),
]

_ROOTS = [
    ("General", "general"),
    ("A330", "a330"),
    ("A300-A600/A310", "a300-a600-a310"),
    ("A320", "a320"),
    ("F100", "f100"),
    ("ATR72-600", "atr72-600"),
]

_OLD_NON_FLEET_ROOT_SLUGS = [
    "iranair",
    "training-and-resources",
    "forms",
    "safety-issue",
]


def _root_id(connection, *, org_id: int, slug: str) -> int | None:
    return connection.execute(
        sa.text(
            """
            SELECT id
            FROM manual_categories
            WHERE org_id = :org_id
              AND parent_id IS NULL
              AND slug = :slug
              AND is_active IS TRUE
            LIMIT 1
            """
        ),
        {"org_id": org_id, "slug": slug},
    ).scalar_one_or_none()


def _create_root(connection, *, org_id: int, name: str, slug: str, sort_order: int) -> int:
    return connection.execute(
        sa.text(
            """
            INSERT INTO manual_categories
                (org_id, parent_id, name, slug, sort_order, is_active)
            VALUES
                (:org_id, NULL, :name, :slug, :sort_order, TRUE)
            RETURNING id
            """
        ),
        {"org_id": org_id, "name": name, "slug": slug, "sort_order": sort_order},
    ).scalar_one()


def _ensure_root(connection, *, org_id: int, name: str, slug: str, sort_order: int) -> int:
    root_id = _root_id(connection, org_id=org_id, slug=slug)
    if root_id is None:
        root_id = _create_root(
            connection,
            org_id=org_id,
            name=name,
            slug=slug,
            sort_order=sort_order,
        )
    else:
        connection.execute(
            sa.text(
                """
                UPDATE manual_categories
                SET name = :name, sort_order = :sort_order, is_active = TRUE
                WHERE id = :id
                """
            ),
            {"id": root_id, "name": name, "sort_order": sort_order},
        )
    return root_id


def _ensure_child(
    connection,
    *,
    org_id: int,
    parent_id: int,
    name: str,
    slug: str,
    sort_order: int,
) -> None:
    child_id = connection.execute(
        sa.text(
            """
            SELECT id
            FROM manual_categories
            WHERE org_id = :org_id
              AND parent_id = :parent_id
              AND slug = :slug
              AND is_active IS TRUE
            LIMIT 1
            """
        ),
        {"org_id": org_id, "parent_id": parent_id, "slug": slug},
    ).scalar_one_or_none()
    if child_id is None:
        connection.execute(
            sa.text(
                """
                INSERT INTO manual_categories
                    (org_id, parent_id, name, slug, sort_order, is_active)
                VALUES
                    (:org_id, :parent_id, :name, :slug, :sort_order, TRUE)
                """
            ),
            {
                "org_id": org_id,
                "parent_id": parent_id,
                "name": name,
                "slug": slug,
                "sort_order": sort_order,
            },
        )
    else:
        connection.execute(
            sa.text(
                """
                UPDATE manual_categories
                SET name = :name, sort_order = :sort_order
                WHERE id = :id
                """
            ),
            {"id": child_id, "name": name, "sort_order": sort_order},
        )


def _normalise_user_aircraft_types(connection) -> None:
    connection.execute(
        sa.text(
            """
            UPDATE users
            SET aircraft_type = CASE
                WHEN aircraft_type IN ('A310', 'A300_600', 'A300-600/310', 'A300/600')
                    THEN 'A300-A600/A310'
                WHEN aircraft_type IN ('ATR', 'ATR 72-600', 'ATR72_600')
                    THEN 'ATR72-600'
                ELSE aircraft_type
            END
            WHERE aircraft_type IN (
                'A310',
                'A300_600',
                'A300-600/310',
                'A300/600',
                'ATR',
                'ATR 72-600',
                'ATR72_600'
            )
            """
        )
    )


def _rename_old_a300_root(connection, *, org_id: int) -> None:
    old_id = _root_id(connection, org_id=org_id, slug="a300-600")
    new_id = _root_id(connection, org_id=org_id, slug="a300-a600-a310")
    if old_id is not None and new_id is None:
        connection.execute(
            sa.text(
                """
                UPDATE manual_categories
                SET name = 'A300-A600/A310',
                    slug = 'a300-a600-a310',
                    sort_order = 3
                WHERE id = :id
                """
            ),
            {"id": old_id},
        )


def _move_old_roots_under_general(connection, *, org_id: int, general_id: int) -> None:
    for slug in _OLD_NON_FLEET_ROOT_SLUGS:
        root_id = _root_id(connection, org_id=org_id, slug=slug)
        if root_id is None:
            continue
        next_sort_order = connection.execute(
            sa.text(
                """
                SELECT COALESCE(MAX(sort_order), 0) + 1
                FROM manual_categories
                WHERE org_id = :org_id
                  AND parent_id = :parent_id
                  AND is_active IS TRUE
                """
            ),
            {"org_id": org_id, "parent_id": general_id},
        ).scalar_one()
        connection.execute(
            sa.text(
                """
                UPDATE manual_categories
                SET parent_id = :parent_id, sort_order = :sort_order
                WHERE id = :id
                """
            ),
            {"id": root_id, "parent_id": general_id, "sort_order": next_sort_order},
        )


def upgrade() -> None:
    """Normalize users and reshape each organization category tree."""
    connection = op.get_bind()
    _normalise_user_aircraft_types(connection)

    org_ids = [row[0] for row in connection.execute(sa.text("SELECT id FROM orgs ORDER BY id"))]
    for org_id in org_ids:
        _rename_old_a300_root(connection, org_id=org_id)

        root_ids: dict[str, int] = {}
        for sort_order, (name, slug) in enumerate(_ROOTS, start=1):
            root_ids[slug] = _ensure_root(
                connection,
                org_id=org_id,
                name=name,
                slug=slug,
                sort_order=sort_order,
            )
            for child_order, (child_name, child_slug) in enumerate(_STANDARD_CHILDREN, start=1):
                _ensure_child(
                    connection,
                    org_id=org_id,
                    parent_id=root_ids[slug],
                    name=child_name,
                    slug=child_slug,
                    sort_order=child_order,
                )

        _move_old_roots_under_general(connection, org_id=org_id, general_id=root_ids["general"])


def downgrade() -> None:
    """Best-effort restoration of the previous root category layout."""
    connection = op.get_bind()
    org_ids = [row[0] for row in connection.execute(sa.text("SELECT id FROM orgs ORDER BY id"))]
    for org_id in org_ids:
        general_id = _root_id(connection, org_id=org_id, slug="general")
        if general_id is not None:
            for sort_order, slug in enumerate(_OLD_NON_FLEET_ROOT_SLUGS, start=2):
                child_id = connection.execute(
                    sa.text(
                        """
                        SELECT id
                        FROM manual_categories
                        WHERE org_id = :org_id
                          AND parent_id = :parent_id
                          AND slug = :slug
                          AND is_active IS TRUE
                        LIMIT 1
                        """
                    ),
                    {"org_id": org_id, "parent_id": general_id, "slug": slug},
                ).scalar_one_or_none()
                if child_id is not None:
                    connection.execute(
                        sa.text(
                            """
                            UPDATE manual_categories
                            SET parent_id = NULL, sort_order = :sort_order
                            WHERE id = :id
                            """
                        ),
                        {"id": child_id, "sort_order": sort_order},
                    )

        a300_id = _root_id(connection, org_id=org_id, slug="a300-a600-a310")
        if a300_id is not None:
            connection.execute(
                sa.text(
                    """
                    UPDATE manual_categories
                    SET name = 'A300/600', slug = 'a300-600', sort_order = 1
                    WHERE id = :id
                    """
                ),
                {"id": a300_id},
            )
