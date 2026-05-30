"""Custom SQLAlchemy column types for PostgreSQL."""

import sqlalchemy.types as types


class CIText(types.UserDefinedType):
    """Maps to PostgreSQL CITEXT (case-insensitive text).

    Requires: CREATE EXTENSION IF NOT EXISTS citext;
    """

    cache_ok = True

    def get_col_spec(self) -> str:
        return "CITEXT"
