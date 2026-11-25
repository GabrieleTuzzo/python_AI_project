from pathlib import Path
from uuid import UUID
from be.notes import Note, load_notes, search_notes, save_notes, delete_note_by_id
from rich.console import Console
from rich.table import Table

def list_notes(notes: list[Note]) -> None:
    if not notes:
        print("No notes found.")
        return

    table = Table(title="Notes")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="bold")
    table.add_column("Content")
    table.add_column("Tags", style="green")

    for note in notes:
        table.add_row(
            str(note.id),
            note.title,
            note.content,
            ", ".join(note.tags) 
            if note.tags
              else "No tags",
        )

    Console().print(table)

def run_notes_cli() -> None:
    path = Path("db") / "notes.json"

    while True:
        notes = load_notes(path)
        action = input("Choose an action: (s)earch, (l)ist notes, (a)dd note, (d)elete note, (q)uit ").strip().lower()
        if action == "q":
            print("Goodbye!")
            break

        elif action == "l":
            list_notes(notes)

        elif action == "s":
            query = input("Search: ").strip()
            list_notes(search_notes(notes, query))

        elif action == "a":
            title = input("Enter note title: ").strip()
            content = input("Enter note content: ").strip()
            tags = []

            if input("Do you want to add tags? (y/n): ").strip().lower() == "y":
                tags = [
                    tag.strip()
                    for tag in input("Enter note tags (comma-separated): ").split(",")
                    if tag.strip()
                ]

            new_note = Note(title=title, content=content, tags=tags)
            notes.append(new_note)
            save_notes(path, notes)

        elif action == "d":
            note_id_str = input("Enter the ID of the note to delete: ").strip()
            try:
                note_id = UUID(note_id_str)
                if not delete_note_by_id(path, note_id):
                    print("Note not found.")
                else:
                    print("Note deleted successfully.")
            except ValueError:
                print("Invalid note ID.")

        else:
            print("Invalid action")


def main() -> None:
    while True:
        print("\nCosa vuoi avviare?")
        print("[1] CLI note")
        print("[2] Server FastAPI + MCP")
        print("[3] Chat Ollama")
        print("[q] Esci")

        choice = input("Scelta: ").strip().lower()

        if choice == "1":
            run_notes_cli()
        elif choice == "2":
            import uvicorn

            uvicorn.run("be.api:app", host="127.0.0.1", port=8000)
        elif choice == "3":
            from be.chat import main as run_chat

            run_chat()
        elif choice == "q":
            print("Arrivederci!")
            break
        else:
            print("Scelta non valida.")

