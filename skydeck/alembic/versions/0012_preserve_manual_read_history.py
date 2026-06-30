"""Preserve manual-read history when current read state is cleared.

Revision ID: 0012
Revises: 0011
Create Date: 2026-06-30

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add current-state fields and backfill manual title snapshots."""
    op.add_column(
        "manual_reads",
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("manual_reads", sa.Column("unread_at", sa.DateTime(timezone=True)))
    op.add_column("manual_reads", sa.Column("manual_title", sa.Text(), nullable=True))

    op.execute(
        """
        UPDATE manual_reads
        SET manual_title = manuals.title
        FROM manuals
        WHERE manual_reads.manual_id = manuals.id
        """
    )
    op.execute("UPDATE manual_reads SET manual_title = '' WHERE manual_title IS NULL")
    op.alter_column("manual_reads", "manual_title", nullable=False)


def downgrade() -> None:
    """Remove current-state fields and title snapshots."""
    op.drop_column("manual_reads", "manual_title")
    op.drop_column("manual_reads", "unread_at")
    op.drop_column("manual_reads", "is_read")
