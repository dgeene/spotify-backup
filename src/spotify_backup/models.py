from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class TrackBackup:
    spotify_id: str | None
    name: str
    artists: list[str]
    album: str | None
    duration_ms: int | None
    isrc: str | None
    spotify_url: str | None
    preview_url: str | None
    added_at: str | None
    is_local: bool
    local_file_name: str | None
    purchase_links: dict[str, str]


@dataclass(frozen=True)
class PlaylistBackup:
    spotify_id: str
    name: str
    description: str | None
    owner_id: str | None
    spotify_url: str | None
    snapshot_id: str | None
    total_tracks: int
    tracks: list[TrackBackup]


@dataclass(frozen=True)
class BackupDocument:
    generated_at: str
    source: str
    playlists: list[PlaylistBackup]

    def to_jsonable(self) -> dict[str, Any]:
        return asdict(self)
