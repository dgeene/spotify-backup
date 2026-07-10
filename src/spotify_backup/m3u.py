from __future__ import annotations

from pathlib import Path
from re import sub

from spotify_backup.models import PlaylistBackup, TrackBackup


def safe_filename(value: str, fallback: str = "playlist") -> str:
    cleaned = sub(r"[^A-Za-z0-9._ -]+", "", value).strip().replace(" ", "_")
    return cleaned or fallback


def expected_audio_filename(track: TrackBackup) -> str:
    artist = track.artists[0] if track.artists else "Unknown Artist"
    title = track.name or "Unknown Title"
    return f"{safe_filename(artist)} - {safe_filename(title)}.mp3"


def render_m3u(playlist: PlaylistBackup, *, audio_root: str | None = None) -> str:
    lines = ["#EXTM3U"]
    for track in playlist.tracks:
        duration_seconds = -1
        if track.duration_ms is not None:
            duration_seconds = max(0, round(track.duration_ms / 1000))
        display = f"{', '.join(track.artists) or 'Unknown Artist'} - {track.name}"
        lines.append(f"#EXTINF:{duration_seconds},{display}")

        if track.local_file_name:
            filename = track.local_file_name
        else:
            filename = expected_audio_filename(track)

        if audio_root:
            lines.append(str(Path(audio_root) / filename))
        else:
            lines.append(filename)
    return "\n".join(lines) + "\n"
