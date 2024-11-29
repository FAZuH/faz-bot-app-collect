FROM ghcr.io/astral-sh/uv:0.5.5-python3.13-bookworm-slim

WORKDIR /app

COPY src ./src
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN uv sync

CMD ["uv", "run", "faz-bot-collect"]
