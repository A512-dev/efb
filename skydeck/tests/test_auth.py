"""Auth endpoint tests – login, refresh, logout, /me, error cases.

Runs against the seeded dev database (SkyWest Regional Airlines).
"""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from tests.conftest import SEED_EMAIL, SEED_PASSWORD


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _login(client: TestClient, email: str = SEED_EMAIL, password: str = SEED_PASSWORD) -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


# ── login ─────────────────────────────────────────────────────


class TestLogin:
    def test_login_success(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": SEED_EMAIL, "password": SEED_PASSWORD},
        )
        assert resp.status_code == 200
        body = resp.json()

        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

        user = body["user"]
        assert user["id"] > 0
        assert user["name"] == "Sarah Mitchell"
        assert user["role"] == "admin"

    def test_login_wrong_password(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": SEED_EMAIL, "password": "wrong"},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert body["error"] == "Invalid email or password"
        assert body["code"] == 401

    def test_login_unknown_email(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "whatever"},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert body["code"] == 401

    def test_login_case_insensitive_email(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "S.MITCHELL@SKYWEST-AIR.COM", "password": SEED_PASSWORD},
        )
        assert resp.status_code == 200
        assert resp.json()["user"]["name"] == "Sarah Mitchell"

    def test_login_with_device_info(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            json={
                "email": SEED_EMAIL,
                "password": SEED_PASSWORD,
                "device_info": {"platform": "iPad", "app_version": "2.0.0"},
            },
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()


class TestSignup:
    def test_admin_can_create_non_pilot_user(self, client: TestClient):
        admin_token = _login(client)
        password = "SkyDeck@2026!"
        email = f"safety-{uuid4().hex[:12]}@example.com"

        signup_resp = client.post(
            "/api/v1/auth/signup",
            json={
                "name": "Safety Officer",
                "email": email,
                "password": password,
                "role": "safety",
            },
            headers=_auth_header(admin_token),
        )

        assert signup_resp.status_code == 201, signup_resp.text
        body = signup_resp.json()
        assert body["user_id"] > 0
        assert body["role"] == "safety"

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert login_resp.status_code == 200, login_resp.text
        assert login_resp.json()["user"]["role"] == "safety"

        delete_resp = client.delete(
            f"/api/v1/users/{body['user_id']}",
            headers=_auth_header(admin_token),
        )
        assert delete_resp.status_code == 200, delete_resp.text

    def test_signup_defaults_to_pilot_role(self, client: TestClient):
        admin_token = _login(client)
        email = f"pilot-{uuid4().hex[:12]}@example.com"

        signup_resp = client.post(
            "/api/v1/auth/signup",
            json={
                "name": "Default Pilot",
                "email": email,
                "password": "SkyDeck@2026!",
            },
            headers=_auth_header(admin_token),
        )

        assert signup_resp.status_code == 201, signup_resp.text
        assert signup_resp.json()["role"] == "pilot"

        delete_resp = client.delete(
            f"/api/v1/users/{signup_resp.json()['user_id']}",
            headers=_auth_header(admin_token),
        )
        assert delete_resp.status_code == 200, delete_resp.text

    def test_signup_requires_admin(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/signup",
            json={
                "name": "No Auth",
                "email": f"no-auth-{uuid4().hex[:12]}@example.com",
                "password": "SkyDeck@2026!",
                "role": "technical",
            },
        )

        assert resp.status_code == 401

    def test_signup_rejects_unknown_role(self, client: TestClient):
        admin_token = _login(client)

        resp = client.post(
            "/api/v1/auth/signup",
            json={
                "name": "Unknown Role",
                "email": f"unknown-{uuid4().hex[:12]}@example.com",
                "password": "SkyDeck@2026!",
                "role": "copilot",
            },
            headers=_auth_header(admin_token),
        )

        assert resp.status_code == 422


# ── refresh ───────────────────────────────────────────────────


class TestRefresh:
    def test_refresh_success(self, client: TestClient, auth_tokens: dict):
        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": auth_tokens["refresh_token"]},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_refresh_invalid_token(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "garbage.token.value"},
        )
        assert resp.status_code == 401
        assert resp.json()["code"] == 401


# ── /me ───────────────────────────────────────────────────────


class TestUsersMe:
    def test_me_authenticated(self, client: TestClient, auth_tokens: dict):
        resp = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == SEED_EMAIL
        assert body["role"] == "admin"
        assert "id" in body
        assert "org_id" in body
        assert "created_at" in body

    def test_me_no_token(self, client: TestClient):
        resp = client.get("/api/v1/users/me")
        assert resp.status_code == 401
        assert resp.json()["code"] == 401

    def test_me_bad_token(self, client: TestClient):
        resp = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )
        assert resp.status_code == 401


# ── logout ────────────────────────────────────────────────────


class TestLogout:
    def test_logout_revokes_session(self, client: TestClient):
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": SEED_EMAIL, "password": SEED_PASSWORD},
        )
        tokens = login_resp.json()

        logout_resp = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert logout_resp.status_code == 200
        assert logout_resp.json()["message"] == "Logged out successfully"

        refresh_resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh_resp.status_code == 401

    def test_logout_with_invalid_token_is_safe(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "garbage"},
        )
        assert resp.status_code == 200
