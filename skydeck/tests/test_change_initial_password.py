"""Integration coverage for the shared-key password replacement flow."""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from tests.conftest import SEED_EMAIL, SEED_PASSWORD

_SIGNUP_KEY = "pytest-signup-key"


def _admin_token(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": SEED_EMAIL, "password": SEED_PASSWORD},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_change_password_with_signup_key(client: TestClient, monkeypatch):
    """A valid key replaces a temporary user's password without touching seed users."""
    monkeypatch.setattr(settings, "SIGNUP_KEY", _SIGNUP_KEY)
    admin_token = _admin_token(client)
    email = f"password-change-{uuid4().hex[:12]}@example.com"
    initial_password = "InitialPassw0rd!"
    new_password = "ReplacementPassw0rd!"

    signup_response = client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Password Change Test",
            "email": email,
            "password": initial_password,
            "role": "technical",
            "position": "Engineer",
            "aircraft_type": "N/A",
        },
        headers=_auth_header(admin_token),
    )
    assert signup_response.status_code == 201, signup_response.text
    user_id = signup_response.json()["user_id"]

    try:
        change_response = client.post(
            "/api/v1/auth/change-password",
            json={
                "email": email,
                "signup_key": _SIGNUP_KEY,
                "new_password": new_password,
            },
        )
        assert change_response.status_code == 200, change_response.text
        assert change_response.json() == {"message": "Password changed successfully"}

        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": new_password},
        )
        assert login_response.status_code == 200, login_response.text
    finally:
        delete_response = client.delete(
            f"/api/v1/users/{user_id}",
            headers=_auth_header(admin_token),
        )
        assert delete_response.status_code == 200, delete_response.text


def test_change_password_rejects_invalid_key(client: TestClient, monkeypatch):
    """A wrong shared key is rejected before user lookup."""
    monkeypatch.setattr(settings, "SIGNUP_KEY", _SIGNUP_KEY)

    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "email": SEED_EMAIL,
            "signup_key": "wrong-signup-key",
            "new_password": "ReplacementPassw0rd!",
        },
    )

    assert response.status_code == 401


def test_change_password_returns_not_found_for_unknown_user(client: TestClient, monkeypatch):
    """A valid shared key returns not found for an absent password target."""
    monkeypatch.setattr(settings, "SIGNUP_KEY", _SIGNUP_KEY)

    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "email": f"missing-{uuid4().hex[:12]}@example.com",
            "signup_key": _SIGNUP_KEY,
            "new_password": "ReplacementPassw0rd!",
        },
    )

    assert response.status_code == 404
