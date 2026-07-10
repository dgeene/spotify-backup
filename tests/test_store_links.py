from spotify_backup.store_links import purchase_search_links


def test_purchase_links_include_encoded_track_query() -> None:
    links = purchase_search_links("Sweet Song", ["The Band"], "First Album")

    assert links["qobuz"].endswith("Sweet+Song+The+Band+First+Album")
    assert "bandcamp.com/search" in links["bandcamp"]
