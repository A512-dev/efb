"""manual update reads

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-07

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "manual_update_reads",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column(
            "org_id",
            sa.BigInteger,
            sa.ForeignKey("orgs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "manual_update_event_id",
            sa.BigInteger,
            sa.ForeignKey("manual_update_events.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint(
            "user_id",
            "manual_update_event_id",
            name="uq_manual_update_reads_user_event",
        ),
    )
    op.create_index("idx_manual_update_reads_org_id", "manual_update_reads", ["org_id"])
    op.create_index("idx_manual_update_reads_user_id", "manual_update_reads", ["user_id"])
    op.create_index(
        "idx_manual_update_reads_event_id",
        "manual_update_reads",
        ["manual_update_event_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_manual_update_reads_event_id", table_name="manual_update_reads")
    op.drop_index("idx_manual_update_reads_user_id", table_name="manual_update_reads")
    op.drop_index("idx_manual_update_reads_org_id", table_name="manual_update_reads")
    op.drop_table("manual_update_reads")
