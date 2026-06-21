"""Add hierarchical organization-scoped categories to the manual library.

The migration creates and seeds a two-level default tree for every existing
organization, assigns all existing manuals to ``Iranair / General``, then makes
``manuals.category_id`` required.

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_CATEGORY_TREE = [
    (
        "A300/600",
        "a300-600",
        [
            ("Aircraft documents", "aircraft-documents"),
            ("Aircraft Performance", "aircraft-performance"),
            ("Fleet memos", "fleet-memos"),
            ("General", "general"),
            ("MEL CDI", "mel-cdi"),
            ("training documents", "training-documents"),
        ],
    ),
    (
        "Iranair",
        "iranair",
        [
            ("Aircraft documents", "aircraft-documents"),
            ("Aircraft Performance", "aircraft-performance"),
            ("Fleet memos", "fleet-memos"),
            ("General", "general"),
            ("MEL CDI", "mel-cdi"),
            ("training documents", "training-documents"),
        ],
    ),
    (
        "Training and resources",
        "training-and-resources",
        [
            ("Aircraft documents", "aircraft-documents"),
            ("Aircraft Performance", "aircraft-performance"),
            ("Fleet memos", "fleet-memos"),
            ("General", "general"),
            ("MEL CDI", "mel-cdi"),
            ("training documents", "training-documents"),
        ],
    ),
    (
        "Forms",
        "forms",
        [
            ("REPORTS", "reports"),
            ("sms", "sms"),
            ("training", "training"),
        ],
    ),
    (
        "Safety Issue",
        "safety-issue",
        [
            ("Aircraft documents", "aircraft-documents"),
            ("Aircraft Performance", "aircraft-performance"),
            ("Fleet memos", "fleet-memos"),
            ("General", "general"),
            ("MEL CDI", "mel-cdi"),
            ("training documents", "training-documents"),
        ],
    ),
]


def _seed_categories(connection) -> None:
    """Seed default roots/children and backfill existing manual category IDs."""
    org_ids = [row[0] for row in connection.execute(sa.text("SELECT id FROM orgs ORDER BY id"))]

    for org_id in org_ids:
        for root_order, (root_name, root_slug, children) in enumerate(_CATEGORY_TREE, start=1):
            root_id = connection.execute(
                sa.text(
                    """
                    INSERT INTO manual_categories
                        (org_id, parent_id, name, slug, sort_order, is_active)
                    VALUES
                        (:org_id, NULL, :name, :slug, :sort_order, TRUE)
                    RETURNING id
                    """
                ),
                {
                    "org_id": org_id,
                    "name": root_name,
                    "slug": root_slug,
                    "sort_order": root_order,
                },
            ).scalar_one()

            for child_order, (child_name, child_slug) in enumerate(children, start=1):
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
                        "parent_id": root_id,
                        "name": child_name,
                        "slug": child_slug,
                        "sort_order": child_order,
                    },
                )

        default_category_id = connection.execute(
            sa.text(
                """
                SELECT child.id
                FROM manual_categories AS child
                JOIN manual_categories AS parent ON parent.id = child.parent_id
                WHERE child.org_id = :org_id
                  AND parent.slug = 'iranair'
                  AND child.slug = 'general'
                LIMIT 1
                """
            ),
            {"org_id": org_id},
        ).scalar_one()

        connection.execute(
            sa.text(
                """
                UPDATE manuals
                SET category_id = :category_id
                WHERE org_id = :org_id AND category_id IS NULL
                """
            ),
            {"category_id": default_category_id, "org_id": org_id},
        )


def upgrade() -> None:
    """Create the category tree, seed it, and require a manual leaf category."""
    op.create_table(
        "manual_categories",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column(
            "org_id",
            sa.BigInteger,
            sa.ForeignKey("orgs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "parent_id",
            sa.BigInteger,
            sa.ForeignKey("manual_categories.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("slug", sa.Text, nullable=False),
        sa.Column("sort_order", sa.Integer, server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_manual_categories_org_id", "manual_categories", ["org_id"])
    op.create_index("idx_manual_categories_parent_id", "manual_categories", ["parent_id"])
    op.create_index(
        "idx_manual_categories_active",
        "manual_categories",
        ["org_id", "is_active"],
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_manual_categories_root_slug
        ON manual_categories (org_id, slug)
        WHERE parent_id IS NULL
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_manual_categories_child_slug
        ON manual_categories (org_id, parent_id, slug)
        WHERE parent_id IS NOT NULL
        """
    )

    op.add_column("manuals", sa.Column("category_id", sa.BigInteger, nullable=True))
    op.create_foreign_key(
        "fk_manuals_category_id_manual_categories",
        "manuals",
        "manual_categories",
        ["category_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("idx_manuals_category_id", "manuals", ["category_id"])

    _seed_categories(op.get_bind())

    op.alter_column("manuals", "category_id", existing_type=sa.BigInteger, nullable=False)


def downgrade() -> None:
    """Remove manual category references and then the category tree."""
    op.drop_index("idx_manuals_category_id", table_name="manuals")
    op.drop_constraint("fk_manuals_category_id_manual_categories", "manuals", type_="foreignkey")
    op.drop_column("manuals", "category_id")

    op.execute("DROP INDEX IF EXISTS uq_manual_categories_child_slug")
    op.execute("DROP INDEX IF EXISTS uq_manual_categories_root_slug")
    op.drop_index("idx_manual_categories_active", table_name="manual_categories")
    op.drop_index("idx_manual_categories_parent_id", table_name="manual_categories")
    op.drop_index("idx_manual_categories_org_id", table_name="manual_categories")
    op.drop_table("manual_categories")
