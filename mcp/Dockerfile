FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

WORKDIR /app
COPY . .

RUN uv sync --no-install-project

CMD ["uv", "run", "main.py"]