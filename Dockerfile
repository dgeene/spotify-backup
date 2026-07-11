FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.5 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    SPOTIFY_BACKUP_DATA_DIR=/data \
    SPOTIFY_BACKUP_TOKEN_FILE=/data/tokens.json

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && poetry install --only main --no-root \
    && poetry install --only-root

VOLUME ["/data"]

CMD ["spotify-backup", "service"]
