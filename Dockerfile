FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SPOTIFY_BACKUP_DATA_DIR=/data \
    SPOTIFY_BACKUP_TOKEN_FILE=/data/tokens.json

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

VOLUME ["/data"]

CMD ["spotify-backup", "service"]
