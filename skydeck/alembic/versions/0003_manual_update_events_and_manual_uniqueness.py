"""Add the manual-update feed and change manual uniqueness semantics.

The original schema made PDF checksums globally unique. This revision allows
identical bytes under different titles and instead enforces one active
case-insensitive title per organization.

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create update events and replace checksum uniqueness with active titles."""
    op.create_table(
        "manual_update_events",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column(
            "org_id",
            sa.BigInteger,
            sa.ForeignKey("orgs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "manual_id",
            sa.BigInteger,
            sa.ForeignKey("manuals.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "actor_user_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("old_storage_path", sa.Text, nullable=True),
        sa.Column("new_storage_path", sa.Text, nullable=True),
        sa.Column("old_sha256", sa.Text, nullable=True),
        sa.Column("new_sha256", sa.Text, nullable=True),
        sa.Column("old_version_number", sa.BigInteger, nullable=True),
        sa.Column("new_version_number", sa.BigInteger, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_manual_update_events_org_id", "manual_update_events", ["org_id"])
    op.create_index("idx_manual_update_events_manual_id", "manual_update_events", ["manual_id"])
    op.create_index(
        "idx_manual_update_events_actor_user_id",
        "manual_update_events",
        ["actor_user_id"],
    )
    op.create_index(
        "idx_manual_update_events_created_at",
        "manual_update_events",
        ["created_at"],
    )

    op.execute("ALTER TABLE manuals DROP CONSTRAINT IF EXISTS manuals_sha256_key")
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_manuals_active_org_title
        ON manuals (org_id, lower(title))
        WHERE deleted_at IS NULL
        """
    )


def downgrade() -> None:
    """Restore checksum uniqueness and remove the manual-update event table."""
    op.execute("DROP INDEX IF EXISTS uq_manuals_active_org_title")
    op.create_unique_constraint("manuals_sha256_key", "manuals", ["sha256"])

    op.drop_index("idx_manual_update_events_created_at", table_name="manual_update_events")
    op.drop_index("idx_manual_update_events_actor_user_id", table_name="manual_update_events")
    op.drop_index("idx_manual_update_events_manual_id", table_name="manual_update_events")
    op.drop_index("idx_manual_update_events_org_id", table_name="manual_update_events")
    op.drop_table("manual_update_events")
