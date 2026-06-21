"""Version 1 of SkyDeck's HTTP API.

Each module exposes a FastAPI ``APIRouter``. :mod:`app.main` mounts those
routers under ``/api/v1``, so route decorators in this package use paths
relative to that shared prefix.
"""
