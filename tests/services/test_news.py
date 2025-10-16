import pytest
import respx
from httpx import Response

from app.services import news


@pytest.fixture(autouse=True)
def reset_cache() -> None:
    news._reset_cache()


@pytest.mark.asyncio
@respx.mock
async def test_fetch_latest_news_success() -> None:
    respx.get(
        news.REDDIT_NEWS_URL,
        params={"limit": 5, "raw_json": 1},
        headers=news.REQUEST_HEADERS,
    ).mock(
        return_value=Response(
            200,
            json={
                "data": {
                    "children": [
                        {
                            "data": {
                                "title": "Tesla announces new model",
                                "url": "https://www.example.com/news/1",
                                "created_utc": 1700000000,
                                "subreddit": "TeslaMotors",
                            }
                        },
                    ]
                }
            },
        )
    )

    items = await news.fetch_latest_news(limit=5)

    assert len(items) == 1
    assert items[0].title == "Tesla announces new model"
    assert items[0].url == "https://www.example.com/news/1"
    assert items[0].source == "r/TeslaMotors"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_latest_news_skips_incomplete_entries() -> None:
    respx.get(
        news.REDDIT_NEWS_URL,
        params={"limit": 5, "raw_json": 1},
        headers=news.REQUEST_HEADERS,
    ).mock(
        return_value=Response(
            200,
            json={
                "data": {
                    "children": [
                        {"data": {"title": None}},
                        {
                            "data": {
                                "title": "Valid",
                                "url": "https://example.com",
                                "created_utc": 1700000000,
                            }
                        },
                    ]
                }
            },
        )
    )

    items = await news.fetch_latest_news()

    assert len(items) == 1
    assert items[0].title == "Valid"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_latest_news_uses_recent_cache() -> None:
    route = respx.get(
        news.REDDIT_NEWS_URL,
        params={"limit": 5, "raw_json": 1},
        headers=news.REQUEST_HEADERS,
    ).mock(
        return_value=Response(
            200,
            json={
                "data": {
                    "children": [
                        {
                            "data": {
                                "title": "Initial",
                                "url": "https://example.com/initial",
                                "created_utc": 1700000000,
                                "subreddit": "TeslaMotors",
                            }
                        }
                    ]
                }
            },
        )
    )

    first = await news.fetch_latest_news()
    second = await news.fetch_latest_news()

    assert route.call_count == 1
    assert first == second


@pytest.mark.asyncio
@respx.mock
async def test_fetch_latest_news_returns_stale_on_failure() -> None:
    route = respx.get(
        news.REDDIT_NEWS_URL,
        params={"limit": 5, "raw_json": 1},
        headers=news.REQUEST_HEADERS,
    ).mock(
        side_effect=[
            Response(
                200,
                json={
                    "data": {
                        "children": [
                            {
                                "data": {
                                    "title": "Cached",
                                    "url": "https://example.com/cached",
                                    "created_utc": 1700000000,
                                    "subreddit": "TeslaMotors",
                                }
                            }
                        ]
                    }
                },
            ),
            Response(503, json={}),
        ]
    )

    cached_items = await news.fetch_latest_news()
    assert news._cached_at is not None
    news._cached_at -= news.CACHE_TTL_SECONDS + 1

    fallback_items = await news.fetch_latest_news()

    assert route.call_count == 2
    assert cached_items == fallback_items
