"""unique employee numbers per organization

Revision ID: 0009
Revises: 0008
Create Date: 2026-06-07

"""
from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNIQUE INDEX uq_users_org_employee_no_active
        ON users (org_id, lower(btrim(employee_no)))
        WHERE deleted_at IS NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX uq_users_org_employee_no_active")
