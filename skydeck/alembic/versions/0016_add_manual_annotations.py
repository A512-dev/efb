"""Add private, version-bound PDF annotations.

Revision ID: 0016
Revises: 0015
Create Date: 2026-07-19

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0016"
down_revision: Union[str, None] = "0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user-owned annotation state without changing manual storage."""
    op.create_table(
        "manual_annotations",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
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
        sa.Column("manual_version_number", sa.Integer, nullable=False),
        sa.Column("annotation_type", sa.Text, nullable=False),
        sa.Column("page_number", sa.Integer, nullable=False),
        sa.Column("geometry_json", postgresql.JSONB, nullable=False),
        sa.Column("style_json", postgresql.JSONB, nullable=False),
        sa.Column("selected_text", sa.Text, nullable=True),
        sa.Column("note_text", sa.Text, nullable=True),
        sa.Column("revision", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "annotation_type IN ("
            "'highlight', 'underline', 'strikeout', 'sticky_note', "
            "'ink', 'rectangle', 'ellipse', 'line'"
            ")",
            name="ck_manual_annotations_type",
        ),
        sa.CheckConstraint(
            "manual_version_number >= 1",
            name="ck_manual_annotations_version",
        ),
        sa.CheckConstraint("page_number >= 1", name="ck_manual_annotations_page"),
        sa.CheckConstraint("revision >= 1", name="ck_manual_annotations_revision"),
        sa.UniqueConstraint(
            "user_id",
            "manual_id",
            "client_id",
            name="uq_manual_annotations_user_manual_client",
        ),
    )
    op.create_index("idx_manual_annotations_org_id", "manual_annotations", ["org_id"])
    op.create_index("idx_manual_annotations_user_id", "manual_annotations", ["user_id"])
    op.create_index("idx_manual_annotations_manual_id", "manual_annotations", ["manual_id"])
    op.create_index(
        "idx_manual_annotations_user_manual_version_active",
        "manual_annotations",
        ["user_id", "manual_id", "manual_version_number"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    """Remove annotation state and its indexes."""
    op.drop_index(
        "idx_manual_annotations_user_manual_version_active",
        table_name="manual_annotations",
    )
    op.drop_index("idx_manual_annotations_manual_id", table_name="manual_annotations")
    op.drop_index("idx_manual_annotations_user_id", table_name="manual_annotations")
    op.drop_index("idx_manual_annotations_org_id", table_name="manual_annotations")
    op.drop_table("manual_annotations")
