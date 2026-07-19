"""Integration coverage for private, version-bound PDF annotations."""

from __future__ import annotations

import io
from copy import deepcopy
from uuid import uuid4

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from app.db.session import SessionLocal
from app.models.manual import Manual
from app.models.manual_annotation import ManualAnnotation
from tests.conftest import SEED_EMAIL, SEED_PASSWORD

PILOT_EMAIL = "a.chen@skywest-air.com"
SECOND_PILOT_EMAIL = "m.rivera@skywest-air.com"
PILOT_PASSWORD = "SkyDeck@2026!"


def _make_pdf(text: str) -> bytes:
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf)
    pdf.drawString(100, 700, text)
    pdf.save()
    buf.seek(0)
    return buf.read()


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _user_id(client: TestClient, token: str) -> int:
    response = client.get("/api/v1/users/me", headers=_headers(token))
    assert response.status_code == 200, response.text
    return response.json()["id"]


def _first_leaf_id(nodes: list[dict]) -> int:
    for node in nodes:
        children = node.get("children", [])
        if children:
            return _first_leaf_id(children)
        return node["id"]
    raise AssertionError("No manual category leaf found")


def _upload_manual(client: TestClient, admin_token: str, title: str) -> int:
    categories = client.get(
        "/api/v1/manual-categories/tree",
        headers=_headers(admin_token),
    )
    assert categories.status_code == 200, categories.text
    response = client.post(
        "/api/v1/manuals/upload",
        data={"title": title, "category_id": str(_first_leaf_id(categories.json()))},
        files={"file": ("annotation_test.pdf", _make_pdf(title), "application/pdf")},
        headers=_headers(admin_token),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _delete_manual(client: TestClient, admin_token: str, manual_id: int) -> None:
    client.delete(f"/api/v1/manuals/{manual_id}", headers=_headers(admin_token))


def _text_payload(user_id: int, annotation_type: str, version: int = 1) -> dict:
    return {
        "user_id": user_id,
        "manual_version_number": version,
        "annotation_type": annotation_type,
        "page_number": 1,
        "geometry": {
            "rects": [{"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.04}]
        },
        "style": {"color": "#FFF176", "opacity": 0.35},
        "selected_text": "Hydraulic pressure",
        "note_text": "Review this section",
    }


def _payloads_for_all_types(user_id: int) -> list[dict]:
    return [
        _text_payload(user_id, "highlight"),
        _text_payload(user_id, "underline"),
        _text_payload(user_id, "strikeout"),
        {
            "user_id": user_id,
            "manual_version_number": 1,
            "annotation_type": "sticky_note",
            "page_number": 1,
            "geometry": {"point": {"x": 0.4, "y": 0.5}},
            "style": {"color": "#FFD54F"},
            "note_text": "Ask training about this procedure",
        },
        {
            "user_id": user_id,
            "manual_version_number": 1,
            "annotation_type": "ink",
            "page_number": 1,
            "geometry": {
                "paths": [[{"x": 0.1, "y": 0.1}, {"x": 0.2, "y": 0.2}]]
            },
            "style": {"stroke_color": "#E53935", "stroke_width": 0.002, "opacity": 1},
        },
        {
            "user_id": user_id,
            "manual_version_number": 1,
            "annotation_type": "rectangle",
            "page_number": 1,
            "geometry": {"bounds": {"x": 0.2, "y": 0.2, "width": 0.2, "height": 0.2}},
            "style": {
                "stroke_color": "#1565C0",
                "stroke_width": 0.002,
                "opacity": 0.8,
                "fill_color": "#BBDEFB",
            },
        },
        {
            "user_id": user_id,
            "manual_version_number": 1,
            "annotation_type": "ellipse",
            "page_number": 1,
            "geometry": {"bounds": {"x": 0.5, "y": 0.5, "width": 0.2, "height": 0.2}},
            "style": {
                "stroke_color": "#2E7D32",
                "stroke_width": 0.002,
                "opacity": 0.8,
                "fill_color": None,
            },
        },
        {
            "user_id": user_id,
            "manual_version_number": 1,
            "annotation_type": "line",
            "page_number": 1,
            "geometry": {"start": {"x": 0.1, "y": 0.8}, "end": {"x": 0.6, "y": 0.8}},
            "style": {"stroke_color": "#212121", "stroke_width": 0.002, "opacity": 1},
        },
    ]


def _manual_storage_state(manual_id: int) -> tuple[str, str, int]:
    with SessionLocal() as db:
        manual = db.query(Manual).filter(Manual.id == manual_id).one()
        return manual.storage_path, manual.sha256, manual.version_number


class TestManualAnnotationCrud:
    def test_all_types_are_private_and_do_not_change_manual_storage(self, client: TestClient):
        admin_token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        pilot_token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)
        second_pilot_token = _login(client, SECOND_PILOT_EMAIL, PILOT_PASSWORD)
        pilot_id = _user_id(client, pilot_token)
        second_pilot_id = _user_id(client, second_pilot_token)
        manual_id = _upload_manual(
            client,
            admin_token,
            f"Annotation CRUD {uuid4().hex}",
        )
        annotation_url = f"/api/v1/manuals/{manual_id}/annotations"
        before_storage = _manual_storage_state(manual_id)

        try:
            payloads = _payloads_for_all_types(pilot_id)
            created = []
            for payload in payloads:
                response = client.post(annotation_url, json=payload, headers=_headers(pilot_token))
                assert response.status_code == 201, response.text
                assert response.json()["user_id"] == pilot_id
                assert "client_id" not in response.json()
                assert "revision" not in response.json()
                created.append(response.json())

            wrong_owner_payload = _text_payload(second_pilot_id, "highlight")
            wrong_owner = client.post(
                annotation_url,
                json=wrong_owner_payload,
                headers=_headers(pilot_token),
            )
            assert wrong_owner.status_code == 403

            mine = client.get(annotation_url, headers=_headers(pilot_token))
            assert mine.status_code == 200, mine.text
            assert mine.json()["user_id"] == pilot_id
            assert mine.json()["manual_version_number"] == 1
            assert len(mine.json()["annotations"]) == 8

            other_user = client.get(annotation_url, headers=_headers(second_pilot_token))
            assert other_user.status_code == 200
            assert other_user.json()["user_id"] == second_pilot_id
            assert other_user.json()["annotations"] == []

            admin_view = client.get(annotation_url, headers=_headers(admin_token))
            assert admin_view.status_code == 200
            assert admin_view.json()["annotations"] == []

            private_update_payload = deepcopy(payloads[0])
            private_update_payload["user_id"] = second_pilot_id
            private_update = client.put(
                f"{annotation_url}/{created[0]['id']}",
                json=private_update_payload,
                headers=_headers(second_pilot_token),
            )
            assert private_update.status_code == 404

            updated_payload = deepcopy(payloads[0])
            updated_payload["note_text"] = "Updated private note"
            update = client.put(
                f"{annotation_url}/{created[0]['id']}",
                json=updated_payload,
                headers=_headers(pilot_token),
            )
            assert update.status_code == 200, update.text
            assert update.json()["note_text"] == "Updated private note"

            deleted = client.delete(
                f"{annotation_url}/{created[0]['id']}",
                headers=_headers(pilot_token),
            )
            assert deleted.status_code == 204

            after_delete = client.get(annotation_url, headers=_headers(pilot_token))
            assert len(after_delete.json()["annotations"]) == 7
            assert _manual_storage_state(manual_id) == before_storage

            download = client.get(
                f"/api/v1/manuals/{manual_id}/download",
                headers=_headers(pilot_token),
            )
            assert download.status_code == 200
            assert download.content.startswith(b"%PDF-")
        finally:
            _delete_manual(client, admin_token, manual_id)

    def test_invalid_geometry_and_authentication_are_rejected(self, client: TestClient):
        admin_token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        pilot_token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)
        pilot_id = _user_id(client, pilot_token)
        manual_id = _upload_manual(client, admin_token, f"Annotation Validation {uuid4().hex}")
        annotation_url = f"/api/v1/manuals/{manual_id}/annotations"

        try:
            assert client.get(annotation_url).status_code == 401

            invalid = _text_payload(pilot_id, "highlight")
            invalid["geometry"]["rects"][0] = {
                "x": 0.9,
                "y": 0.2,
                "width": 0.2,
                "height": 0.1,
            }
            response = client.post(annotation_url, json=invalid, headers=_headers(pilot_token))
            assert response.status_code == 422

            oversized_note = _text_payload(pilot_id, "highlight")
            oversized_note["note_text"] = "x" * 5001
            response = client.post(
                annotation_url,
                json=oversized_note,
                headers=_headers(pilot_token),
            )
            assert response.status_code == 422

            missing_manual = client.get(
                "/api/v1/manuals/999999999/annotations",
                headers=_headers(pilot_token),
            )
            assert missing_manual.status_code == 404
        finally:
            _delete_manual(client, admin_token, manual_id)

    def test_offline_sync_endpoint_is_removed(self, client: TestClient):
        admin_token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        pilot_token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)
        manual_id = _upload_manual(client, admin_token, f"No Annotation Sync {uuid4().hex}")

        try:
            response = client.post(
                f"/api/v1/manuals/{manual_id}/annotations/sync",
                json={"manual_version_number": 1, "changes": []},
                headers=_headers(pilot_token),
            )
            assert response.status_code == 405
        finally:
            _delete_manual(client, admin_token, manual_id)


class TestManualAnnotationVersions:
    def test_replacement_archives_old_annotations(self, client: TestClient):
        admin_token = _login(client, SEED_EMAIL, SEED_PASSWORD)
        pilot_token = _login(client, PILOT_EMAIL, PILOT_PASSWORD)
        pilot_id = _user_id(client, pilot_token)
        manual_id = _upload_manual(client, admin_token, f"Annotation Version {uuid4().hex}")
        annotation_url = f"/api/v1/manuals/{manual_id}/annotations"

        try:
            version_one = _text_payload(pilot_id, "highlight", version=1)
            created = client.post(annotation_url, json=version_one, headers=_headers(pilot_token))
            assert created.status_code == 201, created.text

            replacement = client.post(
                f"/api/v1/manuals/{manual_id}/update",
                files={
                    "file": (
                        "annotation_replacement.pdf",
                        _make_pdf("replacement"),
                        "application/pdf",
                    )
                },
                headers=_headers(admin_token),
            )
            assert replacement.status_code == 200, replacement.text
            assert replacement.json()["version_number"] == 2

            current = client.get(annotation_url, headers=_headers(pilot_token))
            assert current.status_code == 200
            assert current.json()["manual_version_number"] == 2
            assert current.json()["annotations"] == []

            stale = _text_payload(pilot_id, "underline", version=1)
            stale_response = client.post(
                annotation_url,
                json=stale,
                headers=_headers(pilot_token),
            )
            assert stale_response.status_code == 409

            version_two = _text_payload(pilot_id, "underline", version=2)
            fresh = client.post(annotation_url, json=version_two, headers=_headers(pilot_token))
            assert fresh.status_code == 201, fresh.text

            with SessionLocal() as db:
                versions = {
                    row.manual_version_number
                    for row in db.query(ManualAnnotation)
                    .filter(ManualAnnotation.manual_id == manual_id)
                    .all()
                }
            assert versions == {1, 2}
        finally:
            _delete_manual(client, admin_token, manual_id)
