"""add messages

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "messages",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column(
            "org_id",
            sa.BigInteger,
            sa.ForeignKey("orgs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "sender_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "recipient_id",
            sa.BigInteger,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("subject", sa.Text, nullable=True),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_messages_org_id", "messages", ["org_id"])
    op.create_index("idx_messages_sender_id", "messages", ["sender_id"])
    op.create_index("idx_messages_recipient_id", "messages", ["recipient_id"])
    op.create_index("idx_messages_recipient_created", "messages", ["recipient_id", "created_at"])
    op.create_index("idx_messages_sender_created", "messages", ["sender_id", "created_at"])
    op.create_index(
        "idx_messages_unread",
        "messages",
        ["recipient_id"],
        postgresql_where=sa.text("read_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("idx_messages_unread", table_name="messages")
    op.drop_index("idx_messages_sender_created", table_name="messages")
    op.drop_index("idx_messages_recipient_created", table_name="messages")
    op.drop_index("idx_messages_recipient_id", table_name="messages")
    op.drop_index("idx_messages_sender_id", table_name="messages")
    op.drop_index("idx_messages_org_id", table_name="messages")
    op.drop_table("messages")
