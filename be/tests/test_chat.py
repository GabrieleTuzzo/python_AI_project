import pytest
from mcp import Client

import be.mcp_server as mcp_server
from be.chat import execute_tool_call
from be.notes import Note, load_notes, save_notes


@pytest.mark.anyio
async def test_declined_delete_does_not_remove_note(tmp_path, monkeypatch):
    path = tmp_path / "notes.json"
    monkeypatch.setattr(mcp_server, "NOTES_PATH", path)
    note = Note(title="Temporary", content="Keep this note")
    save_notes(path, [note])

    async with Client(mcp_server.mcp) as client:
        result = await execute_tool_call(
            client,
            "delete_note",
            {"note_id": str(note.id)},
            lambda _note_id: False,
        )

    assert result == "Eliminazione annullata dall'utente."
    assert load_notes(path) == [note]


@pytest.mark.anyio
async def test_confirmed_delete_removes_note(tmp_path, monkeypatch):
    path = tmp_path / "notes.json"
    monkeypatch.setattr(mcp_server, "NOTES_PATH", path)
    note = Note(title="Temporary", content="Delete this note")
    save_notes(path, [note])
    confirmed_ids = []

    def confirm(note_id: str) -> bool:
        confirmed_ids.append(note_id)
        return True

    async with Client(mcp_server.mcp) as client:
        result = await execute_tool_call(
            client,
            "delete_note",
            {"note_id": str(note.id)},
            confirm,
        )

    assert confirmed_ids == [str(note.id)]
    assert result == f"Deleted note {note.id}."
    assert load_notes(path) == []
