"""Auth endpoint tests – login, refresh, logout, /me, error cases.

Runs against the seeded dev database (SkyWest Regional Airlines).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import SEED_EMAIL, SEED_PASSWORD

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
