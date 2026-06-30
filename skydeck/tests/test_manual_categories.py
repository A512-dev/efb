"""Integration tests for dynamic manual category administration."""

from __future__ import annotations

import io
import uuid

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from tests.conftest import SEED_EMAIL, SEED_PASSWORD

PILOT_EMAIL = "a.chen@skywest-air.com"
PILOT_PASSWORD = "SkyDeck@2026!"


def _make_pdf(text: str = "manual category test") -> bytes:
    """Generate a tiny valid PDF for manual uploads."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 700, text)
    c.save()
    buf.seek(0)
    return buf.read()


def _login(client: TestClient, email: str = SEED_EMAIL, password: str = SEED_PASSWORD) -> str:
    """Return an access token for a seeded user."""
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    """Build bearer auth headers."""
    return {"Authorization": f"Bearer {token}"}


def _unique_name(prefix: str) -> str:
    """Return a category/manual name unlikely to collide in a persistent DB."""
    return f"{prefix} {uuid.uuid4().hex[:10]}"


def _create_category(
    client: TestClient,
    token: str,
    name: str,
    parent_id: int | None = None,
) -> dict:
    """Create one category and assert success."""
    resp = client.post(
        "/api/v1/manual-categories",
        json={"name": name, "parent_id": parent_id},
        headers=_auth_header(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _delete_category(client: TestClient, token: str, category_id: int) -> None:
    """Best-effort cleanup for empty test categories."""
    client.delete(f"/api/v1/manual-categories/{category_id}", headers=_auth_header(token))


def test_admin_can_manage_empty_category_tree(client: TestClient):
    """Admin can create, rename, reorder, move, and delete empty folders."""
    token = _login(client)
    root = _create_category(client, token, _unique_name("Pytest Root"))
    root_id = root["id"]

    try:
        assert root["is_leaf"] is True
        assert root["has_children"] is False
        original_slug = root["slug"]

        renamed = client.patch(
            f"/api/v1/manual-categories/{root_id}",
            json={"name": _unique_name("Pytest Renamed Root")},
            headers=_auth_header(token),
        )
        assert renamed.status_code == 200, renamed.text
        assert renamed.json()["slug"] == original_slug

        child_a = _create_category(client, token, _unique_name("Pytest Child A"), root_id)
        child_b = _create_category(client, token, _unique_name("Pytest Child B"), root_id)
        child_c = _create_category(client, token, _unique_name("Pytest Child C"), root_id)

        reordered = client.patch(
            "/api/v1/manual-categories/reorder",
            json={
                "parent_id": root_id,
                "category_ids": [child_b["id"], child_a["id"], child_c["id"]],
            },
            headers=_auth_header(token),
        )
        assert reordered.status_code == 200, reordered.text
        assert [item["id"] for item in reordered.json()] == [
            child_b["id"],
            child_a["id"],
            child_c["id"],
        ]

        moved = client.patch(
            f"/api/v1/manual-categories/{child_c['id']}/move",
            json={"parent_id": child_a["id"]},
            headers=_auth_header(token),
        )
        assert moved.status_code == 200, moved.text
        assert moved.json()["parent_id"] == child_a["id"]

        deleted = client.delete(
            f"/api/v1/manual-categories/{root_id}",
            headers=_auth_header(token),
        )
        assert deleted.status_code == 200, deleted.text

        hidden = client.get(
            f"/api/v1/manual-categories/{root_id}/path",
            headers=_auth_header(token),
        )
        assert hidden.status_code == 404
    finally:
        _delete_category(client, token, root_id)


def test_default_roots_are_fleet_first(client: TestClient):
    """The first folder level is General plus the supported fleets."""
    token = _login(client)

    resp = client.get("/api/v1/manual-categories/roots", headers=_auth_header(token))

    assert resp.status_code == 200, resp.text
    root_slugs = [item["slug"] for item in resp.json()]
    assert root_slugs == [
        "general",
        "a330",
        "a300-a600-a310",
        "a320",
        "f100",
        "atr72-600",
    ]


def test_duplicate_active_sibling_name_is_rejected(client: TestClient):
    """Active categories cannot share a display name under the same parent."""
    token = _login(client)
    name = _unique_name("Pytest Duplicate")
    root = _create_category(client, token, name)

    try:
        duplicate = client.post(
            "/api/v1/manual-categories",
            json={"name": name},
            headers=_auth_header(token),
        )
        assert duplicate.status_code == 409
    finally:
        _delete_category(client, token, root["id"])


def test_category_with_manual_cannot_be_deleted_or_gain_children(client: TestClient):
    """Manual-bearing leaf categories remain protected until manuals move/delete."""
    token = _login(client)
    category = _create_category(client, token, _unique_name("Pytest Manual Leaf"))
    manual_id = None

    try:
        upload = client.post(
            "/api/v1/manuals/upload",
            data={"title": _unique_name("Pytest Manual"), "category_id": str(category["id"])},
            files={"file": ("category-test.pdf", _make_pdf(), "application/pdf")},
            headers=_auth_header(token),
        )
        assert upload.status_code == 201, upload.text
        manual_id = upload.json()["id"]

        child = client.post(
            "/api/v1/manual-categories",
            json={"name": _unique_name("Pytest Blocked Child"), "parent_id": category["id"]},
            headers=_auth_header(token),
        )
        assert child.status_code == 409

        deleted = client.delete(
            f"/api/v1/manual-categories/{category['id']}",
            headers=_auth_header(token),
        )
        assert deleted.status_code == 409
    finally:
        if manual_id is not None:
            client.delete(f"/api/v1/manuals/{manual_id}", headers=_auth_header(token))
        _delete_category(client, token, category["id"])


def test_non_admin_cannot_mutate_categories(client: TestClient):
    """Pilot role keeps read access but cannot administer folders."""
    token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)
    resp = client.post(
        "/api/v1/manual-categories",
        json={"name": _unique_name("Pytest Forbidden")},
        headers=_auth_header(token),
    )
    assert resp.status_code == 403
