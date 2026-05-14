"""Shared fixtures for the test suite.

Tests run against the real dev database that was seeded in Phase 1.
The seeded admin user is ``s.mitchell@skywest-air.com`` with
password ``SkyDeck@2026!``.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

SEED_EMAIL = "s.mitchell@skywest-air.com"
SEED_PASSWORD = "SkyDeck@2026!"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def auth_tokens(client: TestClient):
    """Login once and return the full token response dict."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": SEED_EMAIL, "password": SEED_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()
