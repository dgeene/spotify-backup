from __future__ import annotations

import time
from typing import Any, Iterable

import requests

API_URL = "https://api.spotify.com/v1"


class SpotifyClient:
    def __init__(self, access_token: str) -> None:
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})

    def get(self, path_or_url: str, **params: Any) -> dict[str, Any]:
        url = path_or_url if path_or_url.startswith("https://") else f"{API_URL}{path_or_url}"
        while True:
            response = self.session.get(url, params=params or None, timeout=30)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "5"))
                time.sleep(retry_after)
                continue
            response.raise_for_status()
            return response.json()

    def paged(self, path: str, **params: Any) -> Iterable[dict[str, Any]]:
        payload = self.get(path, **params)
        while True:
            yield from payload.get("items", [])
            next_url = payload.get("next")
            if not next_url:
                break
            payload = self.get(next_url)

    def current_user_playlists(self) -> list[dict[str, Any]]:
        return list(self.paged("/me/playlists", limit=50))

    def playlist_items(self, playlist_id: str) -> list[dict[str, Any]]:
        return list(
            self.paged(
                f"/playlists/{playlist_id}/tracks",
                limit=50,
                additional_types="track",
            )
        )
