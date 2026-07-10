from spotify_backup.m3u import render_m3u
from spotify_backup.models import PlaylistBackup, TrackBackup


def test_render_m3u_uses_expected_track_filenames() -> None:
    playlist = PlaylistBackup(
        spotify_id="playlist-1",
        name="Road",
        description=None,
        owner_id=None,
        spotify_url=None,
        snapshot_id=None,
        total_tracks=1,
        tracks=[
            TrackBackup(
                spotify_id="track-1",
                name="A/B Song",
                artists=["An Artist"],
                album="Album",
                duration_ms=123000,
                isrc=None,
                spotify_url=None,
                preview_url=None,
                added_at=None,
                is_local=False,
                local_file_name=None,
                purchase_links={},
            )
        ],
    )

    assert render_m3u(playlist) == (
        "#EXTM3U\n"
        "#EXTINF:123,An Artist - A/B Song\n"
        "An_Artist - AB_Song.mp3\n"
    )
