import json
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

NonBlankText = Annotated[str, Field(min_length=1)]


class NoteCreate(BaseModel):
    title: NonBlankText
    content: NonBlankText
    tags: list[str] = Field(default_factory=list)

    @field_validator("title", "content")
    @classmethod
    def strip_non_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be blank.")
        return value

    @field_validator("tags")
    @classmethod
    def strip_empty_tags(cls, value: list[str]) -> list[str]:
        return [tag.strip() for tag in value if tag.strip()]


class Note(NoteCreate):
    id: UUID = Field(default_factory=uuid4)


def add_note(path: Path, note_data: NoteCreate) -> Note:
    notes = load_notes(path)
    note = Note(**note_data.model_dump())
    notes.append(note)
    save_notes(path, notes)
    return note


def search_notes(notes: list[Note], query: str) -> list[Note]:
    query = query.strip().casefold()
    if not query:
        return []

    return [
        note
        for note in notes
        if query in note.title.casefold()
        or query in note.content.casefold()
        or any(query in tag.casefold() for tag in note.tags)
    ]

def delete_note_by_id(path: Path,note_id: UUID) -> bool:
    notes = load_notes(path)
    updated_notes = [note for note in notes if note.id != note_id]

    if len(updated_notes) == len(notes):
        return False  # Note not found

    save_notes(path, updated_notes)
    return True  # Note deleted


def load_notes(path: Path) -> list[Note]:
    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return []

    raw_data = json.loads(content)
    notes = [Note.model_validate(item) for item in raw_data]

    if any("id" not in item for item in raw_data):
        save_notes(path, notes)

    return notes

def save_notes(path: Path, notes: list[Note]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [note.model_dump(mode="json") for note in notes]
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )