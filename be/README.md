# Notes

Piccolo progetto didattico per esercitarsi con Python, Pydantic, JSON, REST API,
MCP, Ollama e Docker Compose. Le note sono salvate in un file JSON, senza
database.

## Requisiti

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Ollama e il modello `qwen2.5:3b` per usare la chat
- Docker Desktop con Docker Compose per avviare il backend in container

## Setup locale

Dalla root del repository:

```powershell
uv sync
```

Il comando installa le dipendenze dichiarate in `pyproject.toml` usando
`uv.lock`.

## Avvio

Il comando mostra un menu per scegliere l'interfaccia:

```powershell
uv run be
```

- **CLI note**: gestione interattiva di ricerca, elenco, creazione e
  cancellazione.
- **Server FastAPI + MCP**: REST API e MCP Streamable HTTP sulla porta `8000`.
- **Chat Ollama**: chat terminale con `qwen2.5:3b`; usa MCP in memoria nello
  stesso processo. Scrivi `/q` per uscire.

Per usare direttamente la chat:

```powershell
uv run python -m be.chat
```

Ollama deve essere avviato e il modello deve essere disponibile localmente:

```powershell
ollama pull qwen2.5:3b
```

## REST API

La modalità server del menu avvia FastAPI su `127.0.0.1:8000`.

- Documentazione interattiva: <http://127.0.0.1:8000/docs>
- Stato: `GET /health`
- Elenco note: `GET /notes`
- Ricerca: `GET /notes/search?query=python`
- Creazione: `POST /notes`
- Cancellazione: `DELETE /notes/{note_id}`

Esempio di corpo per `POST /notes`:

```json
{
  "title": "Python",
  "content": "Sto imparando Pydantic",
  "tags": ["studio", "python"]
}
```

Pydantic valida i dati; l'ID UUID viene generato dall'applicazione.

## MCP

Il server MCP espone i tool:

- `search_notes`: cerca per titolo, contenuto o tag.
- `create_note`: crea una nota.
- `delete_note`: elimina una nota dato l'UUID.

Quando FastAPI è in esecuzione, i client MCP si collegano tramite Streamable
HTTP all'endpoint:

```text
http://127.0.0.1:8000/mcp
```

La REST API e MCP sono protocolli separati, montati sulla stessa applicazione.
I tool MCP riutilizzano la logica Python delle note; non invocano gli endpoint
REST.

La chat Ollama attuale usa un client MCP in memoria, non l'endpoint HTTP. La
richiesta di conferma della cancellazione viene gestita dalla chat terminale;
un host MCP esterno non eredita automaticamente quella conferma.

## Docker Compose

Costruire l'immagine e avviare il backend:

```powershell
docker compose up --build
```

Il servizio pubblica la porta solo sul loopback del PC:

- REST: <http://127.0.0.1:8000/docs>
- MCP: <http://127.0.0.1:8000/mcp>

Compose monta un volume nominato su `/app/db`, dove viene salvato
`notes.json`. Il volume sopravvive alla rimozione del container:

```powershell
docker compose down
```

`docker compose down -v` elimina anche il volume e le note persistenti.
La cartella locale `db/` è esclusa dal build context, quindi i dati locali
non vengono copiati nell'immagine.

Il binding `127.0.0.1` è adatto allo sviluppo locale, non rende il servizio
autenticato. Prima di esporlo su una rete occorre progettare autenticazione,
autorizzazione e configurazione di trasporto sicura.

## Test

Eseguire tutti i test:

```powershell
uv run pytest
```

I test coprono la persistenza JSON, la validazione, la REST API, i tool MCP,
la conferma della cancellazione nella chat e il menu di avvio. I test usano
file temporanei e non modificano il database locale.

## Struttura

```text
src/be/
  __init__.py    Menu e CLI
  notes.py       Modelli Pydantic e logica condivisa per le note/JSON
  api.py         REST API FastAPI e mount MCP HTTP
  mcp_server.py  Tool MCP
  chat.py        Client Ollama e orchestrazione delle tool call
  prompts.py     System prompt della chat
tests/
  test_api.py
  test_chat.py
  test_launcher.py
  test_mcp.py
  test_notes.py
```

La CLI e la chat locale usano percorsi JSON relativi alla directory di lavoro.
Avviare i comandi dalla root del repository; il container usa `/app` come
directory di lavoro e salva i dati nel volume Compose.