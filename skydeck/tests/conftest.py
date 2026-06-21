"""Shared integration fixtures and seeded credentials for the test suite.

Tests run against the real dev database that was seeded in Phase 1.
The seeded admin user is ``s.mitchell@skywest-air.com`` with
password ``SkyDeck@2026!``.

Because these are integration tests, route mutations can persist between tests.
Tests that create durable records should use unique values and clean up where
practical. Module-scoped fixtures reduce repeated application startup and login
overhead without hiding the real HTTP boundary.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

SEED_EMAIL = "s.mitchell@skywest-air.com"
SEED_PASSWORD = "SkyDeck@2026!"


@pytest.fixture(scope="module")
def client():
    """Create one lifespan-aware FastAPI test client per test module.

    Entering the context executes the same startup database connectivity check
    used by the deployed ASGI application.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def auth_tokens(client: TestClient):
    """Login as the seeded admin and return the full token response dictionary."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": SEED_EMAIL, "password": SEED_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()
