"""Manual Library endpoint tests — upload, list, download, delete, RBAC.

Runs against the seeded dev database. Uses a tiny valid PDF generated
in-memory via reportlab so no external file is needed.
"""

from __future__ import annotations

import io

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from tests.conftest import SEED_EMAIL, SEED_PASSWORD

PILOT_EMAIL = "a.chen@skywest-air.com"
PILOT_PASSWORD = "SkyDeck@2026!"


def _make_pdf(text: str = "test") -> bytes:
    """Generate a minimal valid PDF in memory."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 700, text)
    c.save()
    buf.seek(0)
    return buf.read()


def _login(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── upload ────────────────────────────────────────────────────


class TestUpload:
    def test_admin_upload_success(self, client: TestClient):
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        pdf = _make_pdf("admin upload test")
        resp = client.post(
            "/api/v1/manuals/upload",
            data={"title": "Pytest Upload Manual"},
            files={"file": ("test_manual.pdf", pdf, "application/pdf")},
            headers=_auth_header(token),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Pytest Upload Manual"
        assert body["original_filename"] == "test_manual.pdf"
        assert body["file_size"] > 0
        assert len(body["sha256"]) == 64
        assert body["message"] == "Manual uploaded successfully"

    def test_pilot_upload_forbidden(self, client: TestClient):
        token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)
        pdf = _make_pdf("pilot upload attempt")
        resp = client.post(
            "/api/v1/manuals/upload",
            data={"title": "Should Fail"},
            files={"file": ("fail.pdf", pdf, "application/pdf")},
            headers=_auth_header(token),
        )
        assert resp.status_code == 403
        assert resp.json()["code"] == 403

    def test_upload_non_pdf_rejected(self, client: TestClient):
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        resp = client.post(
            "/api/v1/manuals/upload",
            data={"title": "Bad File"},
            files={"file": ("readme.txt", b"hello world", "text/plain")},
            headers=_auth_header(token),
        )
        assert resp.status_code == 415
        assert "PDF" in resp.json()["error"]

    def test_upload_no_auth(self, client: TestClient):
        pdf = _make_pdf()
        resp = client.post(
            "/api/v1/manuals/upload",
            data={"title": "No Auth"},
            files={"file": ("test.pdf", pdf, "application/pdf")},
        )
        assert resp.status_code == 401


# ── list ──────────────────────────────────────────────────────


class TestList:
    def test_admin_list(self, client: TestClient):
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        resp = client.get("/api/v1/manuals", headers=_auth_header(token))
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) >= 4

    def test_pilot_list(self, client: TestClient):
        token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)
        resp = client.get("/api/v1/manuals", headers=_auth_header(token))
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_no_auth(self, client: TestClient):
        resp = client.get("/api/v1/manuals")
        assert resp.status_code == 401


# ── download with watermark ───────────────────────────────────


class TestDownload:
    def test_download_returns_pdf(self, client: TestClient):
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)

        pdf = _make_pdf("watermark test content")
        upload_resp = client.post(
            "/api/v1/manuals/upload",
            data={"title": "Watermark Test"},
            files={"file": ("wm_test.pdf", pdf, "application/pdf")},
            headers=_auth_header(token),
        )
        manual_id = upload_resp.json()["id"]

        resp = client.get(
            f"/api/v1/manuals/{manual_id}/download",
            headers=_auth_header(token),
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert "X-Watermark-Hash" in resp.headers
        assert len(resp.headers["X-Watermark-Hash"]) == 16
        assert resp.headers["content-disposition"].endswith('.pdf"')
        assert len(resp.content) > 0

    def test_pilot_download(self, client: TestClient):
        admin_token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        pdf = _make_pdf("pilot download test")
        upload_resp = client.post(
            "/api/v1/manuals/upload",
            data={"title": "Pilot DL Test"},
            files={"file": ("pilot_dl.pdf", pdf, "application/pdf")},
            headers=_auth_header(admin_token),
        )
        manual_id = upload_resp.json()["id"]

        pilot_token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)
        resp = client.get(
            f"/api/v1/manuals/{manual_id}/download",
            headers=_auth_header(pilot_token),
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert "X-Watermark-Hash" in resp.headers

    def test_download_nonexistent(self, client: TestClient):
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        resp = client.get(
            "/api/v1/manuals/99999/download",
            headers=_auth_header(token),
        )
        assert resp.status_code == 404

    def test_download_no_auth(self, client: TestClient):
        resp = client.get("/api/v1/manuals/1/download")
        assert resp.status_code == 401


# ── delete ────────────────────────────────────────────────────


class TestDelete:
    def test_admin_delete_success(self, client: TestClient):
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)

        pdf = _make_pdf("delete me")
        upload_resp = client.post(
            "/api/v1/manuals/upload",
            data={"title": "To Be Deleted"},
            files={"file": ("delete_me.pdf", pdf, "application/pdf")},
            headers=_auth_header(token),
        )
        manual_id = upload_resp.json()["id"]

        resp = client.delete(
            f"/api/v1/manuals/{manual_id}",
            headers=_auth_header(token),
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Manual deleted successfully"

        dl_resp = client.get(
            f"/api/v1/manuals/{manual_id}/download",
            headers=_auth_header(token),
        )
        assert dl_resp.status_code == 404

    def test_pilot_delete_forbidden(self, client: TestClient):
        token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)
        resp = client.delete("/api/v1/manuals/1", headers=_auth_header(token))
        assert resp.status_code == 403

    def test_delete_nonexistent(self, client: TestClient):
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        resp = client.delete("/api/v1/manuals/99999", headers=_auth_header(token))
        assert resp.status_code == 404

    def test_delete_no_auth(self, client: TestClient):
        resp = client.delete("/api/v1/manuals/1")
        assert resp.status_code == 401
