"""Limit manual category slug uniqueness to active categories.

Revision ID: 0013
Revises: 0012
Create Date: 2026-06-30

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "0013"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow soft-deleted categories to free their sibling slug."""
    op.execute("DROP INDEX IF EXISTS uq_manual_categories_child_slug")
    op.execute("DROP INDEX IF EXISTS uq_manual_categories_root_slug")
    op.execute(
        """
        CREATE UNIQUE INDEX uq_manual_categories_root_slug
        ON manual_categories (org_id, slug)
        WHERE parent_id IS NULL AND is_active IS TRUE
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_manual_categories_child_slug
        ON manual_categories (org_id, parent_id, slug)
        WHERE parent_id IS NOT NULL AND is_active IS TRUE
        """
    )


def downgrade() -> None:
    """Restore original uniqueness across active and inactive categories."""
    op.execute("DROP INDEX IF EXISTS uq_manual_categories_child_slug")
    op.execute("DROP INDEX IF EXISTS uq_manual_categories_root_slug")
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
