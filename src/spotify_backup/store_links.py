from __future__ import annotations

from urllib.parse import quote_plus


def track_query(name: str, artists: list[str], album: str | None = None) -> str:
    parts = [name, *artists[:2]]
    if album:
        parts.append(album)
    return " ".join(part for part in parts if part).strip()


def purchase_search_links(name: str, artists: list[str], album: str | None = None) -> dict[str, str]:
    query = quote_plus(track_query(name, artists, album))
    return {
        "qobuz": f"https://www.qobuz.com/us-en/search?q={query}",
        "bandcamp": f"https://bandcamp.com/search?q={query}",
        "7digital": f"https://us.7digital.com/search?q={query}",
    }
