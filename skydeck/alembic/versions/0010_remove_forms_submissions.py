"""remove forms and submissions

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-14

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("submission_attachments")
    op.drop_table("submissions")
    op.drop_table("form_versions")
    op.drop_table("form_templates")
    op.execute("DROP TYPE IF EXISTS submission_status")


def downgrade() -> None:
    submission_status = postgresql.ENUM(
        "pending",
        "submitted",
        "delivered",
        "failed",
        name="submission_status",
        create_type=False,
    )
    submission_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "form_templates",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column(
            "org_id", sa.BigInteger, sa.ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_form_templates_org_id", "form_templates", ["org_id"])

    op.create_table(
        "form_versions",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column(
            "template_id",
            sa.BigInteger,
            sa.ForeignKey("form_templates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("schema_json", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint(
            "template_id", "version_number", name="uq_form_versions_template_version"
        ),
        sa.CheckConstraint("version_number >= 1", name="ck_form_versions_version_number"),
    )
    op.create_index("idx_form_versions_template_id", "form_versions", ["template_id"])

    op.create_table(
        "submissions",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column(
            "org_id", sa.BigInteger, sa.ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("user_id", sa.BigInteger, sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "form_version_id", sa.BigInteger, sa.ForeignKey("form_versions.id"), nullable=False
        ),
        sa.Column("data_json", postgresql.JSONB(), nullable=False),
        sa.Column("status", submission_status, server_default="pending"),
        sa.Column("hash_id", sa.Text(), nullable=False, unique=True),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("device_info_json", postgresql.JSONB(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_submissions_org_id", "submissions", ["org_id"])
    op.create_index("idx_submissions_user_id", "submissions", ["user_id"])
    op.create_index("idx_submissions_form_version_id", "submissions", ["form_version_id"])
    op.create_index("idx_submissions_created_at", "submissions", ["created_at"])
    op.create_index("idx_submissions_hash_id", "submissions", ["hash_id"])
    op.create_index("idx_submissions_status", "submissions", ["status"])

    op.create_table(
        "submission_attachments",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column(
            "submission_id",
            sa.BigInteger,
            sa.ForeignKey("submissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("original_filename", sa.Text(), nullable=True),
        sa.Column("mime_type", sa.Text(), nullable=True),
        sa.Column("file_size", sa.BigInteger, nullable=True),
        sa.Column("sha256", sa.Text(), nullable=True),
        sa.Column("attachment_type", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("file_size >= 0", name="ck_attachments_file_size"),
    )
    op.create_index("idx_attachments_submission_id", "submission_attachments", ["submission_id"])
