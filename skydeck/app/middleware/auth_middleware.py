"""Reserved module for authentication middleware.

Authentication currently uses FastAPI dependencies from :mod:`app.core.deps`.
Dependency-based authentication is route-aware and integrates cleanly with
OpenAPI, so no global ASGI middleware is registered here.
"""
