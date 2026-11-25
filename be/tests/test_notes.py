from be.notes import Note, delete_note_by_id, load_notes, save_notes, search_notes
import json
from uuid import UUID

def test_save_and_load_notes(tmp_path):
    path = tmp_path / "notes.json"
    original = [Note(title="Test Note", content="This is a test note.", tags=["test", "note"])]

    save_notes(path, original)

    assert load_notes(path) == original

def test_load_persists_id_for_legacy_note(tmp_path):
    path = tmp_path / "notes.json"
    path.write_text(
        json.dumps([{"title": "Legacy", "content": "Old note", "tags": []}]),
        encoding="utf-8",
    )

    notes = load_notes(path)

    assert isinstance(notes[0].id, UUID)
    saved_data = json.loads(path.read_text(encoding="utf-8"))
    assert saved_data[0]["id"] == str(notes[0].id)


def test_delete_note_by_id(tmp_path):
    path = tmp_path / "notes.json"
    first = Note(title="First", content="One")
    second = Note(title="Second", content="Two")
    save_notes(path, [first, second])

    assert delete_note_by_id(path, first.id) is True
    assert load_notes(path) == [second]
    assert delete_note_by_id(path, first.id) is False


def test_search_notes_matches_title_content_and_tags_case_insensitively():
    note = Note(
        title="Python guide",
        content="Pydantic validation",
        tags=["Junior"],
    )

    assert search_notes([note], "  PYTHON  ") == [note]
    assert search_notes([note], "VALIDATION") == [note]
    assert search_notes([note], "junior") == [note]
    assert search_notes([note], "missing") == []


def test_search_notes_returns_no_results_for_blank_query():
    note = Note(title="Python guide", content="Pydantic validation")

    assert search_notes([note], "   ") == []