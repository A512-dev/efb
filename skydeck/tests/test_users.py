"""User profile endpoint tests."""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from tests.conftest import SEED_EMAIL, SEED_PASSWORD

PILOT_EMAIL = "a.chen@skywest-air.com"
PILOT_PASSWORD = "SkyDeck@2026!"


def _login(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _me(client: TestClient, token: str) -> dict:
    resp = client.get("/api/v1/users/me", headers=_auth_header(token))
    assert resp.status_code == 200, resp.text
    return resp.json()


def _profile_payload(user: dict) -> dict:
    return {
        "employee_no": user["employee_no"],
        "position": user["position"],
        "aircraft_type": user["aircraft_type"],
        "medical_expires_at": user["medical_expires_at"],
        "passport_expires_at": user["passport_expires_at"],
        "license_expires_at": user["license_expires_at"],
    }


class TestUserProfileUpdate:
    def test_update_profile_fields_round_trip(self, client: TestClient):
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
        resp = client.patch("/api/v1/users/me/profile", json={"position": "Captain"})

        assert resp.status_code == 401

    def test_profile_picture_endpoint_remains_separate(self, client: TestClient):
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)

        resp = client.post(
            "/api/v1/users/me/profile-picture",
            files={"file": ("bad.txt", b"not an image", "text/plain")},
            headers=_auth_header(token),
        )

        assert resp.status_code == 415
