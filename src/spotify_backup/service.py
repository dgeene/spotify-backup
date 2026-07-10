from __future__ import annotations

import time

from spotify_backup.auth import valid_access_token
from spotify_backup.backup import build_backup, write_backup
from spotify_backup.config import Settings
from spotify_backup.spotify import SpotifyClient


def run_once(settings: Settings, *, write_m3u: bool = True) -> str:
    access_token = valid_access_token(client_id=settings.client_id, token_file=settings.token_file)
    client = SpotifyClient(access_token)
    document = build_backup(client, settings.playlist_ids)
    backup_dir = write_backup(document, settings.data_dir, write_m3u=write_m3u)
    return str(backup_dir)


def run_forever(settings: Settings, *, interval_hours: float, write_m3u: bool = True) -> None:
    interval_seconds = max(60, int(interval_hours * 3600))
    while True:
        try:
            backup_dir = run_once(settings, write_m3u=write_m3u)
            print(f"Backup complete: {backup_dir}", flush=True)
        except Exception as exc:
            print(f"Backup failed: {exc}", flush=True)
        time.sleep(interval_seconds)
