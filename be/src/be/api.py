from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, HTTPException, status
from be.notes import (
    Note,
    NoteCreate,
    add_note,
    delete_note_by_id,
    load_notes,
    search_notes,
)
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from be.mcp_server import mcp

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    async with mcp.session_manager.run():
        yield

app = FastAPI(title="Notes API", lifespan=lifespan)
NOTES_PATH = Path("db") / "notes.json"

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/notes", response_model=list[Note])
def get_notes() -> list[Note]:
    return load_notes(NOTES_PATH)

@app.get("/notes/search", response_model=list[Note])
def search_notes_endpoint(query: str) -> list[Note]:
    return search_notes(load_notes(NOTES_PATH), query)

@app.post(
    "/notes",
    response_model=Note,
    status_code=status.HTTP_201_CREATED,
)
def create_note(note_create: NoteCreate) -> Note:
    return add_note(NOTES_PATH, note_create)

@app.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_note(note_id: UUID) -> None:
    if not delete_note_by_id(NOTES_PATH, note_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

app.mount("/", mcp.streamable_http_app())