FROM ghcr.io/astral-sh/uv:0.5.13-python3.13-bookworm-slim

LABEL org.opencontainers.image.source = "https://github.com/FAZuH/faz-bot-app-collect"

WORKDIR /app

COPY src ./src
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN uv sync

CMD ["uv", "run", "faz-bot-collect"]
