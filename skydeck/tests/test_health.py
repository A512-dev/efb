"""Minimal smoke test for the unauthenticated process-health endpoint.

This module owns its own client because it does not need seeded login fixtures;
it verifies that the application can be imported and its public liveness route
is mounted.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    """The health route should work without authentication or database fixtures."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "SkyDeck"
