from __future__ import annotations

from pathlib import Path

from agent_watch.models import WatchItem
from agent_watch.state import StateStore


def test_state_store_tracks_seen_urls_and_hashes(tmp_path: Path) -> None:
    store = StateStore(tmp_path / "state.sqlite")
    item = WatchItem(
        title="Agent release",
        url="https://example.com/release?utm_campaign=noise",
        source_name="Vendor",
        source_type="rss",
        summary="Release notes for an agent system.",
    )

    assert not store.has_seen(item)
    store.mark_seen(item)
    assert store.has_seen(item)

    same_canonical_url = item.model_copy(update={"url": "https://example.com/release"})
    assert store.has_seen(same_canonical_url)

