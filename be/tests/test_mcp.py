from uuid import UUID

import pytest
from mcp import Client
from mcp.types import TextContent

import be.mcp_server as mcp_server
from be.notes import Note, load_notes, save_notes


def result_text(result) -> str:
    return "\n".join(
        item.text
        for item in result.content
        if isinstance(item, TextContent)
    )


@pytest.mark.anyio
async def test_search_notes_tool_returns_matching_note(tmp_path, monkeypatch):
    path = tmp_path / "notes.json"
    monkeypatch.setattr(mcp_server, "NOTES_PATH", path)
    note = Note(
        title="Python guide",
        content="Pydantic validation",
        tags=["junior"],
    )
    save_notes(path, [note])

    async with Client(mcp_server.mcp) as client:
        result = await client.call_tool("search_notes", {"query": "PYTHON"})

    assert not result.is_error
    assert str(note.id) in result_text(result)
    assert "Python guide" in result_text(result)
    assert "Pydantic validation" in result_text(result)


@pytest.mark.anyio
async def test_create_note_tool_saves_note_with_clean_tags(tmp_path, monkeypatch):
    path = tmp_path / "notes.json"
    monkeypatch.setattr(mcp_server, "NOTES_PATH", path)

    async with Client(mcp_server.mcp) as client:
        result = await client.call_tool(
            "create_note",
            {
                "title": "  MCP guide  ",
                "content": "  Tool testing  ",
                "tags": [" python ", "", "pydantic"],
            },
        )

    assert not result.is_error
    notes = load_notes(path)
    assert len(notes) == 1
    assert notes[0].title == "MCP guide"
    assert notes[0].content == "Tool testing"
    assert notes[0].tags == ["python", "pydantic"]
    assert isinstance(notes[0].id, UUID)
    assert str(notes[0].id) in result_text(result)


@pytest.mark.anyio
async def test_create_note_tool_rejects_blank_title_without_saving(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "notes.json"
    monkeypatch.setattr(mcp_server, "NOTES_PATH", path)

    async with Client(mcp_server.mcp) as client:
        result = await client.call_tool(
            "create_note",
            {
                "title": "   ",
                "content": "Content",
            },
        )

    assert result.is_error
    assert not path.exists()


@pytest.mark.anyio
async def test_delete_note_tool_removes_note(tmp_path, monkeypatch):
    path = tmp_path / "notes.json"
    monkeypatch.setattr(mcp_server, "NOTES_PATH", path)
    note = Note(title="Temporary", content="Delete me")
    save_notes(path, [note])

    async with Client(mcp_server.mcp) as client:
        result = await client.call_tool(
            "delete_note",
            {"note_id": str(note.id)},
        )

    assert not result.is_error
    assert result_text(result) == f"Deleted note {note.id}."
    assert load_notes(path) == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("note_id", "expected_message"),
    [
        ("not-a-uuid", "Invalid note ID."),
        ("00000000-0000-0000-0000-000000000000", "No note found with that ID."),
    ],
)
async def test_delete_note_tool_reports_invalid_or_missing_id(
    tmp_path,
    monkeypatch,
    note_id,
    expected_message,
):
    path = tmp_path / "notes.json"
    monkeypatch.setattr(mcp_server, "NOTES_PATH", path)

    async with Client(mcp_server.mcp) as client:
        result = await client.call_tool("delete_note", {"note_id": note_id})

    assert not result.is_error
    assert result_text(result) == expected_message
