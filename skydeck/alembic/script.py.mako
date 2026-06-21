"""${message}

Alembic generates this revision from ``script.py.mako``. Replace the generated
upgrade/downgrade bodies with the forward and reverse schema operations, and
expand this docstring to explain data backfills or ordering constraints.

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# Alembic uses these identifiers to place the file in the migration graph.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Move the database forward from ``down_revision`` to this revision."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Reverse this revision when the schema/data change is safely reversible."""
    ${downgrades if downgrades else "pass"}
