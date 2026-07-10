from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_REDIRECT_URI = "http://127.0.0.1:8765/callback"
DEFAULT_SCOPES = ("playlist-read-private", "playlist-read-collaborative")


@dataclass(frozen=True)
class Settings:
    client_id: str
    redirect_uri: str
    data_dir: Path
    token_file: Path
    scopes: tuple[str, ...] = DEFAULT_SCOPES
    playlist_ids: tuple[str, ...] = ()


def _csv(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def load_settings(
    *,
    client_id: str | None = None,
    redirect_uri: str | None = None,
    data_dir: Path | None = None,
    token_file: Path | None = None,
    playlist_ids: tuple[str, ...] | None = None,
) -> Settings:
    load_dotenv()

    resolved_data_dir = data_dir or Path(
        os.getenv("SPOTIFY_BACKUP_DATA_DIR", "~/.local/share/spotify-backup")
    ).expanduser()
    resolved_token_file = token_file or Path(
        os.getenv("SPOTIFY_BACKUP_TOKEN_FILE", str(resolved_data_dir / "tokens.json"))
    ).expanduser()

    resolved_client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID", "")
    if not resolved_client_id:
        raise ValueError("SPOTIFY_CLIENT_ID is required.")

    return Settings(
        client_id=resolved_client_id,
        redirect_uri=redirect_uri or os.getenv("SPOTIFY_REDIRECT_URI", DEFAULT_REDIRECT_URI),
        data_dir=resolved_data_dir,
        token_file=resolved_token_file,
        playlist_ids=playlist_ids if playlist_ids is not None else _csv(os.getenv("SPOTIFY_BACKUP_PLAYLIST_IDS")),
    )
