from __future__ import annotations

import sqlite3
from pathlib import Path

from agent_watch.models import WatchItem
from agent_watch.utils import canonicalize_url, content_hash


class StateStore:
    """Small SQLite store for public-project friendly local state."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def has_seen(self, item: WatchItem) -> bool:
        canonical_url = canonicalize_url(item.url)
        item_hash = content_hash(item.title, item.url, item.summary)
        with self._connect() as conn:
            row = conn.execute(
                "select 1 from seen_items where canonical_url = ? or content_hash = ? limit 1",
                (canonical_url, item_hash),
            ).fetchone()
        return row is not None

    def mark_seen(self, item: WatchItem) -> None:
        canonical_url = canonicalize_url(item.url)
        item_hash = content_hash(item.title, item.url, item.summary)
        with self._connect() as conn:
            conn.execute(
                """
                insert or ignore into seen_items
                    (canonical_url, content_hash, title, source_name, source_type, fetched_at)
                values (?, ?, ?, ?, ?, ?)
                """,
                (
                    canonical_url,
                    item_hash,
                    item.title,
                    item.source_name,
                    item.source_type,
                    item.fetched_at.isoformat(),
                ),
            )

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                create table if not exists seen_items (
                    canonical_url text primary key,
                    content_hash text not null unique,
                    title text not null,
                    source_name text not null,
                    source_type text not null,
                    fetched_at text not null
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

