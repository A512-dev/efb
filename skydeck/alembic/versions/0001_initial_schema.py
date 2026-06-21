"""Create the original SkyDeck schema and PostgreSQL enum/extension types.

This baseline revision establishes tenant, authentication, manual, form,
submission, and audit tables. Later revisions evolve or retire several of
these features; a fresh database still replays this historical starting point
before applying those changes.

Revision ID: 0001
Revises:
Create Date: 2026-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the complete baseline schema in foreign-key dependency order."""
    # ── extensions ─────────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    # ── enum types ─────────────────────────────────────────
    user_role = postgresql.ENUM(
        "pilot", "admin", "safety", "planning", "technical", "chief_pilot",
        name="user_role", create_type=False,
    )
    user_role.create(op.get_bind(), checkfirst=True)

    submission_status = postgresql.ENUM(
        "pending", "submitted", "delivered", "failed",
        name="submission_status", create_type=False,
    )
    submission_status.create(op.get_bind(), checkfirst=True)

    manual_action = postgresql.ENUM(
        "view", "download",
        name="manual_action", create_type=False,
    )
    manual_action.create(op.get_bind(), checkfirst=True)

    # ── 1. orgs ────────────────────────────────────────────
    op.create_table(
        "orgs",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("settings_json", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── 2. users ───────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("org_id", sa.BigInteger, sa.ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("email", sa.Text, nullable=False),  # rendered as CITEXT by ALTER below
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.execute("ALTER TABLE users ALTER COLUMN email TYPE citext")
    op.create_index("idx_users_org_id", "users", ["org_id"])
    op.create_index("idx_users_active", "users", ["id"], postgresql_where=sa.text("deleted_at IS NULL"))

    # ── 3. sessions ────────────────────────────────────────
    op.create_table(
        "sessions",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("user_id", sa.BigInteger, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_info_json", postgresql.JSONB, nullable=True),
        sa.Column("refresh_token_hash", sa.Text, nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_sessions_user_id", "sessions", ["user_id"])
    op.create_index("idx_sessions_expires_at", "sessions", ["expires_at"])

    # ── 4. login_attempts ──────────────────────────────────
    op.create_table(
        "login_attempts",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("org_id", sa.BigInteger, sa.ForeignKey("orgs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", sa.BigInteger, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("email", sa.Text, nullable=True),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("device_info_json", postgresql.JSONB, nullable=True),
        sa.Column("success", sa.Boolean, nullable=False),
        sa.Column("failure_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.execute("ALTER TABLE login_attempts ALTER COLUMN email TYPE citext")
    op.create_index("idx_login_attempts_org_id", "login_attempts", ["org_id"])
    op.create_index("idx_login_attempts_user_id", "login_attempts", ["user_id"])
    op.create_index("idx_login_attempts_created_at", "login_attempts", ["created_at"])
    op.create_index("idx_login_attempts_email_created", "login_attempts", ["email", "created_at"])

    # ── 5. manuals ─────────────────────────────────────────
    op.create_table(
        "manuals",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("org_id", sa.BigInteger, sa.ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("storage_path", sa.Text, nullable=False),
        sa.Column("original_filename", sa.Text, nullable=True),
        sa.Column("mime_type", sa.Text, nullable=True),
        sa.Column("file_size", sa.BigInteger, nullable=True),
        sa.Column("sha256", sa.Text, nullable=True, unique=True),
        sa.Column("version_number", sa.Integer, server_default="1"),
        sa.Column("uploaded_by", sa.BigInteger, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("file_size >= 0", name="ck_manuals_file_size"),
        sa.CheckConstraint("version_number >= 1", name="ck_manuals_version_number"),
    )
    op.create_index("idx_manuals_org_id", "manuals", ["org_id"])
    op.create_index("idx_manuals_uploaded_by", "manuals", ["uploaded_by"])
    op.create_index("idx_manuals_sha256", "manuals", ["sha256"])
    op.create_index("idx_manuals_active", "manuals", ["id"], postgresql_where=sa.text("deleted_at IS NULL"))

    # ── 6. manual_access_logs ──────────────────────────────
    op.create_table(
        "manual_access_logs",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("org_id", sa.BigInteger, sa.ForeignKey("orgs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("manual_id", sa.BigInteger, sa.ForeignKey("manuals.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", sa.BigInteger, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("session_id", sa.BigInteger, sa.ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", manual_action, nullable=False),
        sa.Column("watermark_hash_id", sa.Text, nullable=True),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("device_info_json", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_access_logs_org_id", "manual_access_logs", ["org_id"])
    op.create_index("idx_access_logs_manual_id", "manual_access_logs", ["manual_id"])
    op.create_index("idx_access_logs_user_id", "manual_access_logs", ["user_id"])
    op.create_index("idx_access_logs_session_id", "manual_access_logs", ["session_id"])
    op.create_index("idx_access_logs_created_at", "manual_access_logs", ["created_at"])

    # ── 7. form_templates ──────────────────────────────────
    op.create_table(
        "form_templates",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("org_id", sa.BigInteger, sa.ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_form_templates_org_id", "form_templates", ["org_id"])

    # ── 8. form_versions ───────────────────────────────────
    op.create_table(
        "form_versions",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("template_id", sa.BigInteger, sa.ForeignKey("form_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("schema_json", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("template_id", "version_number", name="uq_form_versions_template_version"),
        sa.CheckConstraint("version_number >= 1", name="ck_form_versions_version_number"),
    )
    op.create_index("idx_form_versions_template_id", "form_versions", ["template_id"])

    # ── 9. submissions ─────────────────────────────────────
    op.create_table(
        "submissions",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("org_id", sa.BigInteger, sa.ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.BigInteger, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("form_version_id", sa.BigInteger, sa.ForeignKey("form_versions.id"), nullable=False),
        sa.Column("data_json", postgresql.JSONB, nullable=False),
        sa.Column("status", submission_status, server_default="pending"),
        sa.Column("hash_id", sa.Text, nullable=False, unique=True),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("device_info_json", postgresql.JSONB, nullable=True),
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

    # ── 10. submission_attachments ─────────────────────────
    op.create_table(
        "submission_attachments",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("submission_id", sa.BigInteger, sa.ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("storage_path", sa.Text, nullable=False),
        sa.Column("original_filename", sa.Text, nullable=True),
        sa.Column("mime_type", sa.Text, nullable=True),
        sa.Column("file_size", sa.BigInteger, nullable=True),
        sa.Column("sha256", sa.Text, nullable=True),
        sa.Column("attachment_type", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("file_size >= 0", name="ck_attachments_file_size"),
    )
    op.create_index("idx_attachments_submission_id", "submission_attachments", ["submission_id"])

    # ── 11. audit_logs ─────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
        sa.Column("org_id", sa.BigInteger, sa.ForeignKey("orgs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", sa.BigInteger, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("target_type", sa.Text, nullable=False),
        sa.Column("target_id", sa.Text, nullable=True),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("device_info_json", postgresql.JSONB, nullable=True),
        sa.Column("metadata_json", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_audit_logs_org_id", "audit_logs", ["org_id"])
    op.create_index("idx_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("idx_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    """Remove baseline tables in reverse dependency order, then enum types."""
    op.drop_table("audit_logs")
    op.drop_table("submission_attachments")
    op.drop_table("submissions")
    op.drop_table("form_versions")
    op.drop_table("form_templates")
    op.drop_table("manual_access_logs")
    op.drop_table("manuals")
    op.drop_table("login_attempts")
    op.drop_table("sessions")
    op.drop_table("users")
    op.drop_table("orgs")

    op.execute("DROP TYPE IF EXISTS manual_action")
    op.execute("DROP TYPE IF EXISTS submission_status")
    op.execute("DROP TYPE IF EXISTS user_role")
