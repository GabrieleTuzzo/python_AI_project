from pathlib import Path

from mcp.server import MCPServer
from uuid import UUID

from be.notes import (
    NonBlankText,
    NoteCreate,
    add_note,
    delete_note_by_id,
    load_notes,
    search_notes as find_notes,
)

mcp = MCPServer("notes")
NOTES_PATH = Path("db") / "notes.json"

@mcp.tool()
def search_notes(query: str) -> str:
    """Search saved notes by title, content, or tags."""
    matches = find_notes(load_notes(NOTES_PATH), query)

    if not matches:
        return "No matching notes found."

    return "\n\n".join(
        f"ID: {note.id}\n"
        f"Title: {note.title}\n"
        f"Content: {note.content}\n"
        f"Tags: {', '.join(note.tags) or 'None'}"
        for note in matches
    )

@mcp.tool()
def create_note(
    title: NonBlankText,
    content: NonBlankText,
    tags: list[str] | None = None,
) -> str:
    """Create and save a note with a title, content, and optional tags."""
    note_data = NoteCreate(
        title=title,
        content=content,
        tags=tags or [],
    )
    note = add_note(NOTES_PATH, note_data)

    return f"Created note '{note.title}' with ID {note.id}."

@mcp.tool()
def delete_note(note_id: str) -> str:
    """The chat application requests confirmation before calling this tool"""
    try:
        parsed_id = UUID(note_id)
    except ValueError:
        return "Invalid note ID."

    if not delete_note_by_id(NOTES_PATH, parsed_id):
        return "No note found with that ID."

    return f"Deleted note {parsed_id}."