import pytest
import respx
from httpx import Response

from src.app.services import news


@pytest.mark.asyncio
@respx.mock
async def test_fetch_latest_news_success() -> None:
    respx.get(
        news.REDDIT_NEWS_URL,
        params={"limit": 5},
        headers={"User-Agent": news.USER_AGENT},
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
    respx.get(news.REDDIT_NEWS_URL).mock(
        return_value=Response(
            200,
            json={
                "data": {
                    "children": [
                        {"data": {"title": None}},
                        {"data": {"title": "Valid", "url": "https://example.com", "created_utc": 1700000000}},
                    ]
                }
            },
        )
    )

    items = await news.fetch_latest_news()

    assert len(items) == 1
    assert items[0].title == "Valid"
