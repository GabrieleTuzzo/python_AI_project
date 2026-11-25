import pytest
import be.api as api
from fastapi.testclient import TestClient

client = TestClient(api.app)


def test_create_search_and_delete_note(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "NOTES_PATH", tmp_path / "notes.json")

    created = client.post(
        "/notes",
        json={
            "title": "FastAPI",
            "content": "Testing the API",
            "tags": ["python"],
        },
    )
    assert created.status_code == 201
    note = created.json()

    assert client.get("/notes").json()[0]["id"] == note["id"]
    assert client.get(
        "/notes/search",
        params={"query": "FASTAPI"},
    ).json()[0]["id"] == note["id"]

    deleted = client.delete(f"/notes/{note['id']}")
    assert deleted.status_code == 204
    assert client.get("/notes").json() == []


def test_delete_missing_note_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "NOTES_PATH", tmp_path / "notes.json")

    response = client.delete(
        "/notes/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "   ", "content": "Valid content"},
        {"title": "Valid title", "content": " \t "},
    ],
)
def test_create_note_rejects_blank_fields_without_saving(
    tmp_path,
    monkeypatch,
    payload,
):
    path = tmp_path / "notes.json"
    monkeypatch.setattr(api, "NOTES_PATH", path)

    response = client.post("/notes", json=payload)

    assert response.status_code == 422
    assert not path.exists()