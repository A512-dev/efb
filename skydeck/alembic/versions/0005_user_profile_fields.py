"""user profile fields

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-07

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("employee_no", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("position", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("aircraft_type", sa.Text(), nullable=True))
    op.add_column(
        "users", sa.Column("medical_expires_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "users", sa.Column("passport_expires_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "users", sa.Column("license_expires_at", sa.DateTime(timezone=True), nullable=True)
    )

    op.execute(
        """
        UPDATE users
        SET
            employee_no = id::text,
            position = CASE
                WHEN role = 'admin' THEN 'Admin'
                WHEN role = 'chief_pilot' THEN 'Chief Pilot'
                WHEN role = 'pilot' AND lower(name) LIKE 'captain%' THEN 'Captain'
                WHEN role = 'pilot' THEN 'P2'
                ELSE initcap(replace(role::text, '_', ' '))
            END,
            aircraft_type = CASE
                WHEN role IN ('pilot', 'chief_pilot') THEN 'A310'
                ELSE 'N/A'
            END,
            medical_expires_at = COALESCE(created_at, now()) + INTERVAL '1 year',
            passport_expires_at = COALESCE(created_at, now()) + INTERVAL '5 years',
            license_expires_at = COALESCE(created_at, now()) + INTERVAL '1 year'
        WHERE employee_no IS NULL
        """
    )

    op.alter_column("users", "employee_no", existing_type=sa.Text(), nullable=False)
    op.alter_column("users", "position", existing_type=sa.Text(), nullable=False)
    op.alter_column("users", "aircraft_type", existing_type=sa.Text(), nullable=False)
    op.alter_column(
        "users",
        "medical_expires_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "users",
        "passport_expires_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "users",
        "license_expires_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("users", "license_expires_at")
    op.drop_column("users", "passport_expires_at")
    op.drop_column("users", "medical_expires_at")
    op.drop_column("users", "aircraft_type")
    op.drop_column("users", "position")
    op.drop_column("users", "employee_no")
