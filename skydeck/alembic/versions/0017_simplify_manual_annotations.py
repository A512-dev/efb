"""Simplify manual annotations for the online-only API.

Revision ID: 0017
Revises: 0016
Create Date: 2026-07-19

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0017"
down_revision: Union[str, None] = "0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove offline client identity and optimistic revision state."""
    op.drop_constraint(
        "uq_manual_annotations_user_manual_client",
        "manual_annotations",
        type_="unique",
    )
    op.drop_constraint(
        "ck_manual_annotations_revision",
        "manual_annotations",
        type_="check",
    )
    op.drop_column("manual_annotations", "client_id")
    op.drop_column("manual_annotations", "revision")


def downgrade() -> None:
    """Restore client UUID and revision columns for the previous API contract."""
    op.add_column(
        "manual_annotations",
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        """
        UPDATE manual_annotations
        SET client_id = md5(
            id::text || ':' || user_id::text || ':' || manual_id::text
        )::uuid
        """
    )
    op.alter_column("manual_annotations", "client_id", nullable=False)

    op.add_column(
        "manual_annotations",
        sa.Column("revision", sa.Integer(), server_default="1", nullable=False),
    )
    op.create_check_constraint(
        "ck_manual_annotations_revision",
        "manual_annotations",
        "revision >= 1",
    )
    op.create_unique_constraint(
        "uq_manual_annotations_user_manual_client",
        "manual_annotations",
        ["user_id", "manual_id", "client_id"],
    )
