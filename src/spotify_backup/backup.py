from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from spotify_backup.m3u import render_m3u, safe_filename
from spotify_backup.models import BackupDocument, PlaylistBackup, TrackBackup
from spotify_backup.spotify import SpotifyClient
from spotify_backup.store_links import purchase_search_links


def normalize_track(item: dict[str, Any]) -> TrackBackup | None:
    track = item.get("track")
    if not track or track.get("type") != "track":
        return None

    artists = [artist["name"] for artist in track.get("artists", []) if artist.get("name")]
    album = track.get("album") or {}
    external_ids = track.get("external_ids") or {}
    spotify_url = (track.get("external_urls") or {}).get("spotify")
    name = track.get("name") or "Unknown Title"
    album_name = album.get("name")

    return TrackBackup(
        spotify_id=track.get("id"),
        name=name,
        artists=artists,
        album=album_name,
        duration_ms=track.get("duration_ms"),
        isrc=external_ids.get("isrc"),
        spotify_url=spotify_url,
        preview_url=track.get("preview_url"),
        added_at=item.get("added_at"),
        is_local=bool(item.get("is_local")),
        local_file_name=None,
        purchase_links=purchase_search_links(name, artists, album_name),
    )


def build_backup(client: SpotifyClient, playlist_ids: tuple[str, ...] = ()) -> BackupDocument:
    playlists = client.current_user_playlists()
    selected_ids = set(playlist_ids)
    selected = [p for p in playlists if not selected_ids or p.get("id") in selected_ids]

    playlist_backups: list[PlaylistBackup] = []
    for playlist in selected:
        playlist_id = playlist["id"]
        tracks = [
            normalized
            for item in client.playlist_items(playlist_id)
            if (normalized := normalize_track(item)) is not None
        ]
        playlist_backups.append(
            PlaylistBackup(
                spotify_id=playlist_id,
                name=playlist.get("name") or playlist_id,
                description=playlist.get("description"),
                owner_id=(playlist.get("owner") or {}).get("id"),
                spotify_url=(playlist.get("external_urls") or {}).get("spotify"),
                snapshot_id=playlist.get("snapshot_id"),
                total_tracks=(playlist.get("tracks") or {}).get("total", len(tracks)),
                tracks=tracks,
            )
        )

    return BackupDocument(
        generated_at=datetime.now(UTC).isoformat(),
        source="spotify",
        playlists=playlist_backups,
    )


def write_backup(document: BackupDocument, data_dir: Path, *, write_m3u: bool = True) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = data_dir / "backups" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    json_path = backup_dir / "playlists.json"
    json_path.write_text(
        json.dumps(document.to_jsonable(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if write_m3u:
        m3u_dir = backup_dir / "m3u"
        m3u_dir.mkdir(exist_ok=True)
        for playlist in document.playlists:
            path = m3u_dir / f"{safe_filename(playlist.name, playlist.spotify_id)}.m3u"
            path.write_text(render_m3u(playlist), encoding="utf-8")

    latest_path = data_dir / "latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
    return backup_dir
