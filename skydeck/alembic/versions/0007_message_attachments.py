"""Add encrypted message-attachment metadata.

Ciphertext remains in external storage. The table records its path, trusted
plaintext metadata, digest, and envelope-encryption fields required to unwrap
the per-file data key.

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-07

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create attachment metadata with tenant/message lookup indexes."""
    op.create_table(
        "message_attachments",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column(
            "org_id",
            sa.BigInteger,
            sa.ForeignKey("orgs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "message_id",
            sa.BigInteger,
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("storage_path", sa.Text, nullable=False),
        sa.Column("original_filename", sa.Text, nullable=True),
        sa.Column("mime_type", sa.Text, nullable=False),
        sa.Column("file_size", sa.BigInteger, nullable=False),
        sa.Column("sha256", sa.Text, nullable=False),
        sa.Column("encrypted_key", sa.Text, nullable=False),
        sa.Column("key_nonce", sa.Text, nullable=False),
        sa.Column("content_nonce", sa.Text, nullable=False),
        sa.Column("encryption_key_id", sa.Text, nullable=False),
        sa.Column("encryption_alg", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("file_size >= 0", name="ck_message_attachments_file_size"),
    )
    op.create_index("idx_message_attachments_org_id", "message_attachments", ["org_id"])
    op.create_index(
        "idx_message_attachments_message_id",
        "message_attachments",
        ["message_id"],
    )


def downgrade() -> None:
    """Drop attachment indexes and metadata table; external files are untouched."""
    op.drop_index("idx_message_attachments_message_id", table_name="message_attachments")
    op.drop_index("idx_message_attachments_org_id", table_name="message_attachments")
    op.drop_table("message_attachments")
