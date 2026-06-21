"""Add encrypted profile-picture metadata and current-picture user link.

Pictures use external encrypted storage. ``users.profile_picture_id`` points to
the currently selected metadata row and becomes null if that row is removed.

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-07

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create picture metadata, then add the nullable current-picture reference."""
    op.create_table(
        "user_profile_pictures",
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
        sa.CheckConstraint("file_size >= 0", name="ck_user_profile_pictures_file_size"),
    )
    op.create_index("idx_user_profile_pictures_org_id", "user_profile_pictures", ["org_id"])
    op.create_index("idx_user_profile_pictures_user_id", "user_profile_pictures", ["user_id"])

    op.add_column("users", sa.Column("profile_picture_id", sa.BigInteger, nullable=True))
    op.create_foreign_key(
        "fk_users_profile_picture_id_user_profile_pictures",
        "users",
        "user_profile_pictures",
        ["profile_picture_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("idx_users_profile_picture_id", "users", ["profile_picture_id"])


def downgrade() -> None:
    """Remove the user reference before dropping picture metadata."""
    op.drop_index("idx_users_profile_picture_id", table_name="users")
    op.drop_constraint(
        "fk_users_profile_picture_id_user_profile_pictures",
        "users",
        type_="foreignkey",
    )
    op.drop_column("users", "profile_picture_id")

    op.drop_index("idx_user_profile_pictures_user_id", table_name="user_profile_pictures")
    op.drop_index("idx_user_profile_pictures_org_id", table_name="user_profile_pictures")
    op.drop_table("user_profile_pictures")
