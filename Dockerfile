# syntax=docker/dockerfile:1.7
#
# Build:
#   docker build --platform=linux/amd64 -t agent-fin:local .
#
# Run (local smoke test):
#   docker run --rm -p 8080:8080 \
#     --env-file ../.env \
#     -e AWS_REGION=us-east-1 \
#     -v $HOME/.aws:/home/app/.aws:ro \
#     agent-fin:local
#
# AWS deploy: --platform=linux/amd64 keeps the image compatible with
# Fargate amd64 + App Runner (App Runner only supports amd64). On Fargate
# arm64 you'd rebuild without the platform pin.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Install dependencies first so they cache across code-only changes.
COPY pyproject.toml ./
RUN uv pip install -r pyproject.toml

# Non-root runtime user.
RUN useradd -m -u 1000 app

# App code + bundled KB. .dockerignore filters venv/.git/.env/etc.
COPY --chown=app:app . .

USER app

EXPOSE 8080

# Use sh -c so $PORT expands at container start (Fargate/App Runner
# inject PORT differently, but defaulting to 8080 keeps things simple).
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
