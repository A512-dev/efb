"""Custom SQLAlchemy column types for PostgreSQL.

These classes teach SQLAlchemy how to emit database-specific type names that
are not represented by the generic type API used by the models.
"""

import sqlalchemy.types as types


class CIText(types.UserDefinedType):
    """Maps to PostgreSQL CITEXT (case-insensitive text).

    Requires: CREATE EXTENSION IF NOT EXISTS citext;
    """

    cache_ok = True

    def get_col_spec(self) -> str:
        """Return the exact type declaration used in generated SQL."""
        return "CITEXT"
