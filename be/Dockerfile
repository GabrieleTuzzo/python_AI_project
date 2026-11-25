FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

ENV UV_NO_DEV=1

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --locked

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "be.api:app", "--host", "0.0.0.0", "--port", "8000"]