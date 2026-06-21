"""Integration tests for self-service profiles and admin user management.

The profile round-trip test restores the seeded admin in ``finally`` so later
tests and local development retain the expected seed values.
"""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from tests.conftest import SEED_EMAIL, SEED_PASSWORD

PILOT_EMAIL = "a.chen@skywest-air.com"
PILOT_PASSWORD = "SkyDeck@2026!"


def _login(client: TestClient, email: str, password: str) -> str:
    """Login a seeded user and return their access token."""
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    """Build a standard Bearer authorization header."""
    return {"Authorization": f"Bearer {token}"}


def _me(client: TestClient, token: str) -> dict:
    """Fetch and assert the current-user response before returning JSON."""
    resp = client.get("/api/v1/users/me", headers=_auth_header(token))
    assert resp.status_code == 200, resp.text
    return resp.json()


def _profile_payload(user: dict) -> dict:
    """Extract only fields accepted by the profile PATCH endpoint."""
    return {
        "employee_no": user["employee_no"],
        "position": user["position"],
        "aircraft_type": user["aircraft_type"],
        "medical_expires_at": user["medical_expires_at"],
        "passport_expires_at": user["passport_expires_at"],
        "license_expires_at": user["license_expires_at"],
    }


class TestUserProfileUpdate:
    """Partial updates, uniqueness conflicts, auth, and picture separation."""

    def test_update_profile_fields_round_trip(self, client: TestClient):
        """Editable profile fields round-trip and the seed profile is restored."""
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        original = _me(client, token)
        update = {
            "employee_no": f"pytest-{uuid4().hex[:12]}",
            "position": "Training Captain",
            "aircraft_type": "A320",
            "medical_expires_at": "2031-01-02",
            "passport_expires_at": "2032-03-04T00:00:00+00:00",
            "license_expires_at": "2033-05-06T00:00:00+00:00",
        }

        try:
            resp = client.patch(
                "/api/v1/users/me/profile",
                json=update,
                headers=_auth_header(token),
            )
            assert resp.status_code == 200, resp.text
            body = resp.json()
            assert body["employee_no"] == update["employee_no"]
            assert body["position"] == update["position"]
            assert body["aircraft_type"] == update["aircraft_type"]
            assert body["medical_expires_at"].startswith("2031-01-02T00:00:00")
            assert "profile_picture_url" in body
        finally:
            restore_resp = client.patch(
                "/api/v1/users/me/profile",
                json=_profile_payload(original),
                headers=_auth_header(token),
            )
            assert restore_resp.status_code == 200, restore_resp.text

    def test_update_to_same_employee_no_succeeds(self, client: TestClient):
        """A user may keep their own employee number without a false conflict."""
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        current = _me(client, token)

        resp = client.patch(
            "/api/v1/users/me/profile",
            json={"employee_no": current["employee_no"]},
            headers=_auth_header(token),
        )

        assert resp.status_code == 200, resp.text
        assert resp.json()["employee_no"] == current["employee_no"]

    def test_duplicate_employee_no_returns_friendly_error(self, client: TestClient):
        """Another active user's employee number produces the public 409 shape."""
        admin_token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        pilot_token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)
        pilot = _me(client, pilot_token)

        resp = client.patch(
            "/api/v1/users/me/profile",
            json={"employee_no": pilot["employee_no"]},
            headers=_auth_header(admin_token),
        )

        assert resp.status_code == 409
        assert resp.json() == {"error": "Employee ID is taken.", "code": 409}

    def test_update_profile_requires_auth(self, client: TestClient):
        """Anonymous clients cannot alter profile fields."""
        resp = client.patch("/api/v1/users/me/profile", json={"position": "Captain"})

        assert resp.status_code == 401

    def test_profile_picture_endpoint_remains_separate(self, client: TestClient):
        """Picture validation remains isolated from ordinary profile PATCH data."""
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)

        resp = client.post(
            "/api/v1/users/me/profile-picture",
            files={"file": ("bad.txt", b"not an image", "text/plain")},
            headers=_auth_header(token),
        )

        assert resp.status_code == 415


class TestAdminUserManagement:
    """Tenant user listing, RBAC, soft deletion, and self-delete prevention."""

    def test_admin_can_list_users(self, client: TestClient):
        """Admin listing exposes operational fields but never password hashes."""
        admin_token = _login(client, SEED_EMAIL, SEED_PASSWORD)

        resp = client.get("/api/v1/users", headers=_auth_header(admin_token))

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert any(user["email"] == SEED_EMAIL for user in body)
        assert "medical_expires_at" in body[0]
        assert "passport_expires_at" in body[0]
        assert "license_expires_at" in body[0]
        assert "password_hash" not in body[0]

    def test_pilot_cannot_list_users(self, client: TestClient):
        """Pilot authentication does not grant organization-directory access."""
        pilot_token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)

        resp = client.get("/api/v1/users", headers=_auth_header(pilot_token))

        assert resp.status_code == 403

    def test_admin_can_delete_user(self, client: TestClient):
        """Soft-deleted users disappear from listings and can no longer login."""
        admin_token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        password = "SkyDeck@2026!"
        email = f"delete-{uuid4().hex[:12]}@example.com"

        signup_resp = client.post(
            "/api/v1/auth/signup",
            json={"name": "Delete Me", "email": email, "password": password},
            headers=_auth_header(admin_token),
        )
        assert signup_resp.status_code == 201, signup_resp.text
        user_id = signup_resp.json()["user_id"]

        delete_resp = client.delete(
            f"/api/v1/users/{user_id}",
            headers=_auth_header(admin_token),
        )

        assert delete_resp.status_code == 200, delete_resp.text
        assert delete_resp.json()["message"] == "User deleted successfully"

        list_resp = client.get("/api/v1/users", headers=_auth_header(admin_token))
        assert list_resp.status_code == 200, list_resp.text
        assert all(user["id"] != user_id for user in list_resp.json())

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert login_resp.status_code == 401

    def test_admin_cannot_delete_self(self, client: TestClient):
        """The final active admin cannot accidentally delete their own session user."""
        admin_token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        admin = _me(client, admin_token)

        resp = client.delete(
            f"/api/v1/users/{admin['id']}",
            headers=_auth_header(admin_token),
        )

        assert resp.status_code == 409
        assert resp.json() == {
            "error": "Admins cannot delete their own account",
            "code": 409,
        }
