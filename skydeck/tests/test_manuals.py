"""Manual-library integration tests for upload, list, download, delete, and RBAC.

Runs against the seeded dev database. Uses a tiny valid PDF generated
in-memory via reportlab so no external file is needed.

Tests exercise the complete HTTP/storage/database/watermark path. Titles are
chosen for test readability; repeated local runs may require a freshly seeded
database when a prior run left created manuals behind.
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
    """Return a bearer access token for a seeded test user."""
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    """Build the Authorization header expected by protected endpoints."""
    return {"Authorization": f"Bearer {token}"}


# ── upload ────────────────────────────────────────────────────


class TestUpload:
    """Admin success plus role, authentication, and file-format rejection."""

    def test_admin_upload_success(self, client: TestClient):
        """An admin can persist a valid PDF and receive trusted metadata."""
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
        """A pilot is authenticated but lacks upload permission."""
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
        """Filename/MIME claims cannot disguise non-PDF bytes."""
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
        """Uploading requires an authenticated administrator."""
        pdf = _make_pdf()
        resp = client.post(
            "/api/v1/manuals/upload",
            data={"title": "No Auth"},
            files={"file": ("test.pdf", pdf, "application/pdf")},
        )
        assert resp.status_code == 401


# ── list ──────────────────────────────────────────────────────


class TestList:
    """Authenticated manual visibility for administrative and pilot roles."""

    def test_admin_list(self, client: TestClient):
        """An admin can list seeded and test-created active manuals."""
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        resp = client.get("/api/v1/manuals", headers=_auth_header(token))
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) >= 4

    def test_pilot_list(self, client: TestClient):
        """Pilots share read access to the organization manual library."""
        token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)
        resp = client.get("/api/v1/manuals", headers=_auth_header(token))
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_no_auth(self, client: TestClient):
        """Manual metadata is not publicly listable."""
        resp = client.get("/api/v1/manuals")
        assert resp.status_code == 401


# ── download with watermark ───────────────────────────────────


class TestDownload:
    """Watermarked PDF responses, pilot access, and missing/auth failures."""

    def test_download_returns_pdf(self, client: TestClient):
        """Download returns PDF bytes and a 16-character forensic hash."""
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
        """A pilot can download an admin-uploaded manual."""
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
        """Unknown manual IDs return the standard 404 response."""
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        resp = client.get(
            "/api/v1/manuals/99999/download",
            headers=_auth_header(token),
        )
        assert resp.status_code == 404

    def test_download_no_auth(self, client: TestClient):
        """Manual PDF bytes require authentication."""
        resp = client.get("/api/v1/manuals/1/download")
        assert resp.status_code == 401


# ── delete ────────────────────────────────────────────────────


class TestDelete:
    """Admin soft/physical deletion and role/auth/not-found behavior."""

    def test_admin_delete_success(self, client: TestClient):
        """An admin deletion makes a previously uploaded manual unavailable."""
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
        """A pilot cannot delete manual metadata or files."""
        token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)
        resp = client.delete("/api/v1/manuals/1", headers=_auth_header(token))
        assert resp.status_code == 403

    def test_delete_nonexistent(self, client: TestClient):
        """Deleting an unknown manual returns 404."""
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        resp = client.delete("/api/v1/manuals/99999", headers=_auth_header(token))
        assert resp.status_code == 404

    def test_delete_no_auth(self, client: TestClient):
        """Anonymous callers cannot delete manuals."""
        resp = client.delete("/api/v1/manuals/1")
        assert resp.status_code == 401
