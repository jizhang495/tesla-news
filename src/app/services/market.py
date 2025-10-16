"""Stock market data retrieval for Tesla."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
USER_AGENT = "TeslaDashboard/0.1 (+https://localhost)"
FALLBACK_PRICE = 249.99
FALLBACK_CHANGE = None
FALLBACK_PERCENT_CHANGE = None
FALLBACK_MARKET_STATE = "OFFLINE"


@dataclass(slots=True)
class StockQuote:
    """Represents the most recent stock quote for a symbol."""

    symbol: str
    price: float
    currency: str
    market_time: datetime
    change: float | None = None
    percent_change: float | None = None
    market_state: str | None = None
    is_fallback: bool = False


async def fetch_stock_quote(symbol: str) -> StockQuote:
    """Fetch the latest stock quote for ``symbol`` from Yahoo Finance."""
    params = {"symbols": symbol}
    headers = {"User-Agent": USER_AGENT}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(YAHOO_QUOTE_URL, params=params, headers=headers)
        response.raise_for_status()
    except httpx.HTTPError:
        return _fallback_quote(symbol)

    try:
        payload = response.json()
    except ValueError:
        return _fallback_quote(symbol)

    try:
        quote = _parse_quote(payload, symbol)
    except ValueError:
        return _fallback_quote(symbol)
    return quote


def _parse_quote(payload: Any, symbol: str) -> StockQuote:
    try:
        result = payload["quoteResponse"]["result"]
        item = result[0]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("Unexpected payload structure from quote API") from exc

    price_raw = item.get("regularMarketPrice")
    market_time_raw = item.get("regularMarketTime")
    if price_raw is None or market_time_raw is None:
        raise ValueError("Quote payload missing price or timestamp")

    market_time = datetime.fromtimestamp(int(market_time_raw), tz=timezone.utc)
    change = item.get("regularMarketChange")
    percent_change = item.get("regularMarketChangePercent")

    return StockQuote(
        symbol=symbol.upper(),
        price=float(price_raw),
        currency=item.get("currency", "USD"),
        market_time=market_time,
        change=float(change) if change is not None else None,
        percent_change=float(percent_change) if percent_change is not None else None,
        market_state=item.get("marketState"),
        is_fallback=False,
    )


def _fallback_quote(symbol: str) -> StockQuote:
    """Provide a deterministic offline quote when the live feed is unavailable."""
    return StockQuote(
        symbol=symbol.upper(),
        price=float(FALLBACK_PRICE),
        currency="USD",
        market_time=datetime.now(tz=timezone.utc),
        change=float(FALLBACK_CHANGE) if FALLBACK_CHANGE is not None else None,
        percent_change=(
            float(FALLBACK_PERCENT_CHANGE) if FALLBACK_PERCENT_CHANGE is not None else None
        ),
        market_state=FALLBACK_MARKET_STATE,
        is_fallback=True,
    )


__all__ = ["StockQuote", "fetch_stock_quote"]
