"""FastAPI entrypoint for the Tesla dashboard."""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

from .services.market import StockQuote, fetch_stock_quote
from .services.news import NewsItem, fetch_latest_news

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

app = FastAPI(
    title="Tesla Dashboard",
    description="Displays the latest Tesla stock quote and recent news.",
)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """Render the homepage with stock quote and news."""
    quote: StockQuote | None = None
    news_items: list[NewsItem] = []
    quote_error: str | None = None
    quote_warning: str | None = None
    news_error: str | None = None

    stock_task = asyncio.create_task(fetch_stock_quote("TSLA"))
    news_task = asyncio.create_task(fetch_latest_news(limit=5))
    quote_result, news_result = await asyncio.gather(
        stock_task, news_task, return_exceptions=True
    )

    if isinstance(quote_result, Exception):
        quote_error = "Failed to load stock price. Please try again shortly."
    else:
        quote = quote_result
        if quote.is_fallback:
            quote_warning = "Live price temporarily unavailable; showing cached data."

    if isinstance(news_result, Exception):
        news_error = "Failed to load news. Please try again shortly."
    else:
        news_items = news_result

    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "quote": quote,
            "quote_error": quote_error,
            "quote_warning": quote_warning,
            "news_items": news_items,
            "news_error": news_error,
        },
    )


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    """Return an empty 204 response for the favicon to avoid noisy 404s."""
    return Response(status_code=204)


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple liveness endpoint for container or process checks."""
    return {"status": "ok"}
