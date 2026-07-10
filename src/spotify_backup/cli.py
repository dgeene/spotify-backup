from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer

from spotify_backup.auth import run_login
from spotify_backup.config import load_settings
from spotify_backup.service import run_forever, run_once

app = typer.Typer(no_args_is_help=True, help="Back up Spotify playlists to JSON and M3U.")


ClientIdOption = Annotated[
    str | None,
    typer.Option("--client-id", help="Spotify app Client ID. Defaults to SPOTIFY_CLIENT_ID."),
]
RedirectUriOption = Annotated[
    str | None,
    typer.Option("--redirect-uri", help="OAuth redirect URI allowlisted in Spotify."),
]
DataDirOption = Annotated[
    Path | None,
    typer.Option("--data-dir", help="Directory for backups. Defaults to SPOTIFY_BACKUP_DATA_DIR."),
]
TokenFileOption = Annotated[
    Path | None,
    typer.Option("--token-file", help="OAuth token file. Defaults to SPOTIFY_BACKUP_TOKEN_FILE."),
]


@app.command()
def auth(
    client_id: ClientIdOption = None,
    redirect_uri: RedirectUriOption = None,
    data_dir: DataDirOption = None,
    token_file: TokenFileOption = None,
    no_browser: Annotated[bool, typer.Option("--no-browser", help="Print the URL only.")] = False,
) -> None:
    """Authorize Spotify and store a refresh token."""
    settings = load_settings(
        client_id=client_id,
        redirect_uri=redirect_uri,
        data_dir=data_dir,
        token_file=token_file,
    )
    run_login(
        client_id=settings.client_id,
        redirect_uri=settings.redirect_uri,
        scopes=settings.scopes,
        token_file=settings.token_file,
        open_browser=not no_browser,
    )
    typer.echo(f"Token saved to {settings.token_file}")


@app.command()
def backup(
    client_id: ClientIdOption = None,
    redirect_uri: RedirectUriOption = None,
    data_dir: DataDirOption = None,
    token_file: TokenFileOption = None,
    playlist_id: Annotated[
        list[str] | None,
        typer.Option("--playlist-id", help="Playlist ID to include. Repeat for multiple playlists."),
    ] = None,
    no_m3u: Annotated[bool, typer.Option("--no-m3u", help="Skip M3U export.")] = False,
) -> None:
    """Run one backup now."""
    settings = load_settings(
        client_id=client_id,
        redirect_uri=redirect_uri,
        data_dir=data_dir,
        token_file=token_file,
        playlist_ids=tuple(playlist_id or ()),
    )
    backup_dir = run_once(settings, write_m3u=not no_m3u)
    typer.echo(f"Backup complete: {backup_dir}")


@app.command()
def service(
    client_id: ClientIdOption = None,
    redirect_uri: RedirectUriOption = None,
    data_dir: DataDirOption = None,
    token_file: TokenFileOption = None,
    interval_hours: Annotated[
        float | None,
        typer.Option("--interval-hours", help="Hours between backups."),
    ] = None,
    no_m3u: Annotated[bool, typer.Option("--no-m3u", help="Skip M3U export.")] = False,
) -> None:
    """Run backups forever on an interval."""
    settings = load_settings(
        client_id=client_id,
        redirect_uri=redirect_uri,
        data_dir=data_dir,
        token_file=token_file,
    )
    resolved_interval_hours = interval_hours or float(os.getenv("SPOTIFY_BACKUP_INTERVAL_HOURS", "24"))
    run_forever(settings, interval_hours=resolved_interval_hours, write_m3u=not no_m3u)


if __name__ == "__main__":
    app()
