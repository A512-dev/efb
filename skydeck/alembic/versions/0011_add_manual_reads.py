"""add manual reads

Revision ID: 0011
Revises: 0010
Create Date: 2026-06-21

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "manual_reads",
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
            "manual_id",
            sa.BigInteger,
            sa.ForeignKey("manuals.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_read_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("read_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "manual_id", name="uq_manual_reads_user_manual"),
    )
    op.create_index("idx_manual_reads_org_id", "manual_reads", ["org_id"])
    op.create_index("idx_manual_reads_manual_id", "manual_reads", ["manual_id"])
    op.create_index("idx_manual_reads_user_id", "manual_reads", ["user_id"])
    op.create_index("idx_manual_reads_last_read_at", "manual_reads", ["last_read_at"])


def downgrade() -> None:
    op.drop_index("idx_manual_reads_last_read_at", table_name="manual_reads")
    op.drop_index("idx_manual_reads_user_id", table_name="manual_reads")
    op.drop_index("idx_manual_reads_manual_id", table_name="manual_reads")
    op.drop_index("idx_manual_reads_org_id", table_name="manual_reads")
    op.drop_table("manual_reads")
