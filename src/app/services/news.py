"""Fetch latest Tesla related news items."""

from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

REDDIT_NEWS_URL = "https://www.reddit.com/r/TeslaMotors/new.json"
MAX_NEWS_LIMIT = 20
CACHE_TTL_SECONDS = 120
USER_AGENT = os.getenv(
    "TESLA_NEWS_USER_AGENT",
    "TeslaDashboard/0.1 (+https://github.com/jz/tesla-news)",
)
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
}

_CACHE_LOCK = asyncio.Lock()
_cached_items: list[NewsItem] = []
_cached_at: float | None = None


@dataclass(slots=True)
class NewsItem:
    """Represents a news entry surfaced to the dashboard."""

    title: str
    url: str
    source: str
    published_at: datetime


async def fetch_latest_news(limit: int = 5) -> list[NewsItem]:
    """Fetch latest Tesla news from the Reddit community feed with a short-lived cache."""
    bounded_limit = max(1, min(limit, MAX_NEWS_LIMIT))
    cached = _get_cached_items(bounded_limit)
    if cached is not None:
        return cached

    async with _CACHE_LOCK:
        cached = _get_cached_items(bounded_limit)
        if cached is not None:
            return cached

        params = {"limit": bounded_limit, "raw_json": 1}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(REDDIT_NEWS_URL, params=params, headers=REQUEST_HEADERS)
            response.raise_for_status()
            payload = response.json()
            items = _parse_news(payload)
        except (httpx.HTTPError, ValueError):
            stale = _get_cached_items(bounded_limit, allow_stale=True)
            if stale is not None:
                return stale
            raise

        _store_cache(items)
        return items[:bounded_limit]


def _parse_news(payload: Any) -> list[NewsItem]:
    try:
        entries = payload["data"]["children"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Unexpected payload structure from news API") from exc

    items: list[NewsItem] = []
    for entry in entries:
        post = entry.get("data", {})
        title = post.get("title")
        url = post.get("url")
        created = post.get("created_utc")
        if title is None or url is None or created is None:
            continue
        published_at = datetime.fromtimestamp(int(created), tz=timezone.utc)
        source = f"r/{post.get('subreddit', 'TeslaMotors')}"
        items.append(
            NewsItem(
                title=title,
                url=url,
                source=source,
                published_at=published_at,
            )
        )

    return items


def _store_cache(items: list[NewsItem]) -> None:
    global _cached_items, _cached_at
    _cached_items = list(items)
    _cached_at = time.monotonic()


def _get_cached_items(limit: int, *, allow_stale: bool = False) -> list[NewsItem] | None:
    if not _cached_items:
        return None
    if _cached_at is None:
        return None
    if not allow_stale and time.monotonic() - _cached_at > CACHE_TTL_SECONDS:
        return None
    capped_limit = min(limit, len(_cached_items))
    return [*_cached_items[:capped_limit]]


def _reset_cache() -> None:
    """Test helper to clear cached responses."""
    global _cached_items, _cached_at
    _cached_items = []
    _cached_at = None


__all__ = ["NewsItem", "fetch_latest_news"]
