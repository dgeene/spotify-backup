# spotify-backup

Back up Spotify playlists to JSON, export M3U playlists for portable players, and attach search links for legal downloads from stores such as Qobuz.

This project intentionally stores metadata and playlist structure. It does not download Spotify audio.

## Features

- Spotify OAuth 2.0 Authorization Code with PKCE.
- Periodic Docker service for unattended backups.
- JSON backup documents with playlist, track, ISRC, Spotify URL, and purchase-search metadata.
- M3U export with predictable filenames for locally purchased audio files.
- Store search links for Qobuz, Bandcamp, and 7digital.
- CLI-first structure with reusable modules for a future web UI.
- Handles Spotify pagination and basic rate-limit retries.

## Spotify OAuth Setup

Spotify's OAuth flow is easiest if you treat the first login as an interactive setup step and the Docker service as the later unattended step.

1. Create an app in the Spotify Developer Dashboard.
2. Copy the app's Client ID.
3. Add this Redirect URI exactly:

   ```text
   http://127.0.0.1:8765/callback
   ```

4. Create a `.env` file:

   ```sh
   cp .env.example .env
   ```

5. Put your Client ID in `.env`:

   ```text
   SPOTIFY_CLIENT_ID=your_client_id_here
   ```

6. Install locally and authorize:

   ```sh
   python -m venv .venv
   . .venv/bin/activate
   pip install -e .
   spotify-backup auth --data-dir ./data --token-file ./data/tokens.json
   ```

The CLI starts a tiny local callback server, prints a Spotify authorization URL, and usually opens it in your browser. After you approve access, Spotify redirects back to the local callback and the app stores a refresh token at `./data/tokens.json`.

Required scopes:

- `playlist-read-private` for private playlists.
- `playlist-read-collaborative` for collaborative playlists.

## Run A Backup

```sh
spotify-backup backup --data-dir ./data --token-file ./data/tokens.json
```

Backups are written to:

```text
data/backups/YYYYMMDDTHHMMSSZ/playlists.json
data/backups/YYYYMMDDTHHMMSSZ/m3u/*.m3u
data/latest.json
```

To back up only specific playlists:

```sh
spotify-backup backup --playlist-id spotify_playlist_id
```

## Docker Service

Authorize locally first so `./data/tokens.json` exists. Then run:

```sh
docker compose up --build -d
```

By default the container backs up every 24 hours. Change `SPOTIFY_BACKUP_INTERVAL_HOURS` in `.env` to adjust the interval.

## M3U Strategy

M3U files point at expected local filenames, for example:

```text
Artist_Name - Track_Title.mp3
```

This works well for portable MP3 players after you legally purchase/download the tracks and copy them next to the playlist, or adjust paths with a future `audio_root` option. JSON backups include store search links to help find purchasable MP3/FLAC versions.

## Suggested Next Features

- Match purchased files by ISRC and duration, then fill `local_file_name` automatically.
- Generate a missing-tracks report for tracks not found in your local music folder.
- Add a playlist diff command to show changes between backup snapshots.
- Add restore/export helpers for other formats such as CSV, XSPF, and JSPF.
- Add optional Qobuz API integration if you have legitimate API access.
- Add healthcheck and Prometheus-style metrics for the Docker service.
- Add a small web UI reusing the existing auth/client/backup modules.

## Useful Spotify Docs

- Authorization Code with PKCE: https://developer.spotify.com/documentation/web-api/tutorials/code-pkce-flow
- Get Current User's Playlists: https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists
- Get Playlist Items: https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks
