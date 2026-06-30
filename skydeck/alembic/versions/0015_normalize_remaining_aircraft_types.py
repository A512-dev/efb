"""Normalize any remaining non-enum user aircraft values.

Revision ID: 0015
Revises: 0014
Create Date: 2026-06-30

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0015"
down_revision: Union[str, None] = "0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ensure every active response can serialize through AircraftType."""
    op.execute(
        sa.text(
            """
            UPDATE users
            SET aircraft_type = CASE
                WHEN aircraft_type IN ('A310', 'A300_600', 'A300-600/310', 'A300/600')
                    THEN 'A300-A600/A310'
                WHEN aircraft_type IN ('ATR', 'ATR 72-600', 'ATR72_600')
                    THEN 'ATR72-600'
                WHEN role IN ('pilot', 'chief_pilot')
                     AND aircraft_type NOT IN (
                        'A330',
                        'A300-A600/A310',
                        'A320',
                        'F100',
                        'ATR72-600'
                     )
                    THEN 'A300-A600/A310'
                WHEN role NOT IN ('pilot', 'chief_pilot')
                     AND aircraft_type NOT IN (
                        'A330',
                        'A300-A600/A310',
                        'A320',
                        'F100',
                        'ATR72-600',
                        'N/A'
                     )
                    THEN 'N/A'
                ELSE aircraft_type
            END
            WHERE aircraft_type NOT IN (
                'A330',
                'A300-A600/A310',
                'A320',
                'F100',
                'ATR72-600',
                'N/A'
            )
            """
        )
    )


def downgrade() -> None:
    """Data normalization is intentionally not reversible."""
    pass
