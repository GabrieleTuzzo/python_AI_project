# Notes

Progetto didattico per imparare Python, Pydantic, API REST e MCP, con un
frontend previsto in `fe/`.

## Backend

Il backend si trova in [`be/`](./be/README.md). Da PowerShell, installa le
dipendenze e avvia il menu CLI:

```powershell
cd be
uv sync
uv run be
```

Il menu permette di avviare la CLI delle note, il server FastAPI + MCP o la
chat locale con Ollama. Per requisiti e dettagli d'uso consulta il
[README del backend](./be/README.md).

## Docker Compose

Dalla root del repository:

```powershell
docker compose up --build
```

La REST API è disponibile su <http://127.0.0.1:8000/docs> e l'endpoint MCP
Streamable HTTP su <http://127.0.0.1:8000/mcp>. Le note sono conservate nel
volume Compose `notes_data`; `docker compose down -v` elimina anche il volume.

## Test

Dalla cartella `be/`:

```powershell
uv run pytest
```

Il `.gitignore` nella root esclude dati locali (`be/db/`), ambienti virtuali,
`node_modules` e file `.env`.
