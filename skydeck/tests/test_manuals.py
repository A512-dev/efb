"""Manual-library integration tests for upload, list, download, delete, and RBAC.

Runs against the seeded dev database. Uses a tiny valid PDF generated
in-memory via reportlab so no external file is needed.

Tests exercise the complete HTTP/storage/database/watermark path. Titles are
chosen for test readability; repeated local runs may require a freshly seeded
database when a prior run left created manuals behind.
"""

from __future__ import annotations

import io
from uuid import uuid4

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


def _first_leaf_id(node: dict) -> int:
    """Return the first leaf category id inside a category subtree."""
    children = node.get("children") or []
    if not children:
        return node["id"]
    return _first_leaf_id(children[0])


def _leaf_category_id(client: TestClient, token: str, *, root_slug: str = "general") -> int:
    """Fetch one uploadable leaf below a root category slug."""
    resp = client.get("/api/v1/manual-categories/tree", headers=_auth_header(token))
    assert resp.status_code == 200, resp.text
    root = next((item for item in resp.json() if item["slug"] == root_slug), None)
    assert root is not None, f"Root category {root_slug!r} not found"
    return _first_leaf_id(root)


# ── upload ────────────────────────────────────────────────────


class TestUpload:
    """Admin success plus role, authentication, and file-format rejection."""

    def test_admin_upload_success(self, client: TestClient):
        """An admin can persist a valid PDF and receive trusted metadata."""
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        title = f"Pytest Upload Manual {uuid4().hex[:12]}"
        pdf = _make_pdf("admin upload test")
        resp = client.post(
            "/api/v1/manuals/upload",
            data={
                "title": title,
                "category_id": str(_leaf_category_id(client, token)),
            },
            files={"file": ("test_manual.pdf", pdf, "application/pdf")},
            headers=_auth_header(token),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == title
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
            data={
                "title": "Should Fail",
                "category_id": str(_leaf_category_id(client, _login(client, SEED_EMAIL, SEED_PASSWORD))),
            },
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
            data={
                "title": "Bad File",
                "category_id": str(_leaf_category_id(client, token)),
            },
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
            data={"title": "No Auth", "category_id": "1"},
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


class TestFleetVisibility:
    """Crew users only see General plus their own aircraft root."""

    def test_pilot_is_restricted_to_own_fleet_and_general(self, client: TestClient):
        """Direct IDs from another fleet are hidden from list, read, and download."""
        admin_token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        suffix = uuid4().hex[:12]
        email = f"pytest-a320-fleet-{suffix}@example.com"
        password = "SkyDeck@2026!"

        signup_resp = client.post(
            "/api/v1/auth/signup",
            json={
                "name": "Pytest A320 Pilot",
                "email": email,
                "password": password,
                "role": "pilot",
                "aircraft_type": "A320",
            },
            headers=_auth_header(admin_token),
        )
        assert signup_resp.status_code == 201, signup_resp.text
        user_id = signup_resp.json()["user_id"]
        pilot_token = signup_resp.json()["access_token"]

        a320_id = None
        a330_id = None
        try:
            a320_resp = client.post(
                "/api/v1/manuals/upload",
                data={
                    "title": f"Pytest A320 Fleet Manual {suffix}",
                    "category_id": str(_leaf_category_id(client, admin_token, root_slug="a320")),
                },
                files={"file": ("a320_fleet.pdf", _make_pdf("a320"), "application/pdf")},
                headers=_auth_header(admin_token),
            )
            assert a320_resp.status_code == 201, a320_resp.text
            a320_id = a320_resp.json()["id"]

            a330_resp = client.post(
                "/api/v1/manuals/upload",
                data={
                    "title": f"Pytest A330 Fleet Manual {suffix}",
                    "category_id": str(_leaf_category_id(client, admin_token, root_slug="a330")),
                },
                files={"file": ("a330_fleet.pdf", _make_pdf("a330"), "application/pdf")},
                headers=_auth_header(admin_token),
            )
            assert a330_resp.status_code == 201, a330_resp.text
            a330_id = a330_resp.json()["id"]

            list_resp = client.get("/api/v1/manuals", headers=_auth_header(pilot_token))
            assert list_resp.status_code == 200, list_resp.text
            listed_ids = {item["id"] for item in list_resp.json()}
            assert a320_id in listed_ids
            assert a330_id not in listed_ids

            allowed_download = client.get(
                f"/api/v1/manuals/{a320_id}/download",
                headers=_auth_header(pilot_token),
            )
            assert allowed_download.status_code == 200, allowed_download.text

            hidden_download = client.get(
                f"/api/v1/manuals/{a330_id}/download",
                headers=_auth_header(pilot_token),
            )
            assert hidden_download.status_code == 404

            hidden_read = client.post(
                f"/api/v1/manuals/{a330_id}/read",
                headers=_auth_header(pilot_token),
            )
            assert hidden_read.status_code == 404
        finally:
            if a320_id is not None:
                client.delete(f"/api/v1/manuals/{a320_id}", headers=_auth_header(admin_token))
            if a330_id is not None:
                client.delete(f"/api/v1/manuals/{a330_id}", headers=_auth_header(admin_token))
            client.delete(f"/api/v1/users/{user_id}", headers=_auth_header(admin_token))


# ── download with watermark ───────────────────────────────────


class TestDownload:
    """Watermarked PDF responses, pilot access, and missing/auth failures."""

    def test_download_returns_pdf(self, client: TestClient):
        """Download returns PDF bytes and a 16-character forensic hash."""
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        title = f"Watermark Test {uuid4().hex[:12]}"

        pdf = _make_pdf("watermark test content")
        upload_resp = client.post(
            "/api/v1/manuals/upload",
            data={
                "title": title,
                "category_id": str(_leaf_category_id(client, token)),
            },
            files={"file": ("wm_test.pdf", pdf, "application/pdf")},
            headers=_auth_header(token),
        )
        assert upload_resp.status_code == 201, upload_resp.text
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
        title = f"Pilot DL Test {uuid4().hex[:12]}"
        pdf = _make_pdf("pilot download test")
        upload_resp = client.post(
            "/api/v1/manuals/upload",
            data={
                "title": title,
                "category_id": str(_leaf_category_id(client, admin_token)),
            },
            files={"file": ("pilot_dl.pdf", pdf, "application/pdf")},
            headers=_auth_header(admin_token),
        )
        assert upload_resp.status_code == 201, upload_resp.text
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
        title = f"To Be Deleted {uuid4().hex[:12]}"

        pdf = _make_pdf("delete me")
        upload_resp = client.post(
            "/api/v1/manuals/upload",
            data={
                "title": title,
                "category_id": str(_leaf_category_id(client, token)),
            },
            files={"file": ("delete_me.pdf", pdf, "application/pdf")},
            headers=_auth_header(token),
        )
        assert upload_resp.status_code == 201, upload_resp.text
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
