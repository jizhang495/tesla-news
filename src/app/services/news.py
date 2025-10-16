"""Fetch latest Tesla related news items."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

REDDIT_NEWS_URL = "https://www.reddit.com/r/TeslaMotors/new.json"
USER_AGENT = "TeslaDashboard/0.1 (+https://localhost)"


@dataclass(slots=True)
class NewsItem:
    """Represents a news entry surfaced to the dashboard."""

    title: str
    url: str
    source: str
    published_at: datetime


async def fetch_latest_news(limit: int = 5) -> list[NewsItem]:
    """Fetch latest Tesla news from the Reddit community feed."""
    params = {"limit": max(1, min(limit, 20))}
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(REDDIT_NEWS_URL, params=params, headers=headers)
    response.raise_for_status()
    payload = response.json()
    return _parse_news(payload)


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


__all__ = ["NewsItem", "fetch_latest_news"]
