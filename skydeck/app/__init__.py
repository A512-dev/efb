"""SkyDeck backend application package.

The package is intentionally split into layers:

* :mod:`app.api` translates HTTP requests and responses.
* :mod:`app.services` implements business workflows.
* :mod:`app.repositories` contains database queries and persistence operations.
* :mod:`app.models` defines SQLAlchemy tables and relationships.
* :mod:`app.schemas` defines the Pydantic objects exposed by the API.
* :mod:`app.core` and :mod:`app.db` hold shared infrastructure.

Start with :mod:`app.main` to see how these pieces are assembled into FastAPI.
"""
