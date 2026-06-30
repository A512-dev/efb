"""Integration tests for current and historical manual-read state."""

from __future__ import annotations

import io
from uuid import uuid4

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from tests.conftest import SEED_EMAIL, SEED_PASSWORD


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


def _first_leaf_id(nodes: list[dict]) -> int:
    """Return the first category without children from a category tree."""
    for node in nodes:
        children = node.get("children", [])
        if children:
            return _first_leaf_id(children)
        return node["id"]
    raise AssertionError("No manual category leaf found")


def _leaf_category_id(client: TestClient, token: str) -> int:
    """Fetch one uploadable manual category through the public API."""
    resp = client.get("/api/v1/manual-categories/tree", headers=_auth_header(token))
    assert resp.status_code == 200, resp.text
    return _first_leaf_id(resp.json())


def _upload_manual(client: TestClient, token: str, *, title: str) -> int:
    """Upload one uniquely named manual and return its ID."""
    pdf = _make_pdf(title)
    resp = client.post(
        "/api/v1/manuals/upload",
        data={
            "title": title,
            "category_id": str(_leaf_category_id(client, token)),
        },
        files={"file": ("manual_read_test.pdf", pdf, "application/pdf")},
        headers=_auth_header(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _delete_manual(client: TestClient, token: str, manual_id: int) -> None:
    """Best-effort cleanup for manuals created by these tests."""
    client.delete(f"/api/v1/manuals/{manual_id}", headers=_auth_header(token))


class TestManualReads:
    """Read, unread, and replacement reset behavior."""

    def test_unread_keeps_manual_read_row(self, client: TestClient):
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        title = f"Manual Read Unread {uuid4().hex}"
        manual_id = _upload_manual(client, token, title=title)

        try:
            read_resp = client.post(
                f"/api/v1/manuals/{manual_id}/read",
                headers=_auth_header(token),
            )
            assert read_resp.status_code == 200, read_resp.text
            read_body = read_resp.json()
            assert read_body["manual_id"] == manual_id
            assert read_body["manual_title"] == title
            assert read_body["is_read"] is True
            assert read_body["unread_at"] is None

            unread_resp = client.post(
                f"/api/v1/manuals/{manual_id}/unread",
                headers=_auth_header(token),
            )
            assert unread_resp.status_code == 200, unread_resp.text
            unread_body = unread_resp.json()
            assert unread_body["id"] == read_body["id"]
            assert unread_body["manual_id"] == manual_id
            assert unread_body["manual_title"] == title
            assert unread_body["is_read"] is False
            assert unread_body["unread_at"] is not None

            my_reads_resp = client.get("/api/v1/manuals/reads/me", headers=_auth_header(token))
            assert my_reads_resp.status_code == 200, my_reads_resp.text
            matching_rows = [
                item for item in my_reads_resp.json() if item["manual_id"] == manual_id
            ]
            assert len(matching_rows) == 1
            assert matching_rows[0]["is_read"] is False
        finally:
            _delete_manual(client, token, manual_id)

    def test_manual_update_marks_current_read_unread(self, client: TestClient):
        token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        old_title = f"Manual Read Replace Old {uuid4().hex}"
        new_title = f"Manual Read Replace New {uuid4().hex}"
        manual_id = _upload_manual(client, token, title=old_title)

        try:
            read_resp = client.post(
                f"/api/v1/manuals/{manual_id}/read",
                headers=_auth_header(token),
            )
            assert read_resp.status_code == 200, read_resp.text
            read_body = read_resp.json()
            assert read_body["is_read"] is True
            assert read_body["manual_title"] == old_title

            update_resp = client.post(
                f"/api/v1/manuals/{manual_id}/update",
                data={"title": new_title},
                files={"file": ("manual_read_update.pdf", _make_pdf(new_title), "application/pdf")},
                headers=_auth_header(token),
            )
            assert update_resp.status_code == 200, update_resp.text

            my_reads_resp = client.get("/api/v1/manuals/reads/me", headers=_auth_header(token))
            assert my_reads_resp.status_code == 200, my_reads_resp.text
            replaced_row = next(
                item for item in my_reads_resp.json() if item["manual_id"] == manual_id
            )
            assert replaced_row["id"] == read_body["id"]
            assert replaced_row["is_read"] is False
            assert replaced_row["unread_at"] is not None
            assert replaced_row["manual_title"] == old_title

            reread_resp = client.post(
                f"/api/v1/manuals/{manual_id}/read",
                headers=_auth_header(token),
            )
            assert reread_resp.status_code == 200, reread_resp.text
            reread_body = reread_resp.json()
            assert reread_body["id"] == read_body["id"]
            assert reread_body["is_read"] is True
            assert reread_body["unread_at"] is None
            assert reread_body["manual_title"] == new_title
            assert reread_body["read_count"] == read_body["read_count"] + 1
        finally:
            _delete_manual(client, token, manual_id)
