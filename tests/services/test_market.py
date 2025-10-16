import httpx
import pytest
import respx
from httpx import Response

from app.services import market


@pytest.mark.asyncio
@respx.mock
async def test_fetch_stock_quote_success() -> None:
    route = respx.get(
        market.YAHOO_QUOTE_URL,
        params={"symbols": "TSLA"},
        headers={"User-Agent": market.USER_AGENT},
    ).mock(
        return_value=Response(
            200,
            json={
                "quoteResponse": {
                    "result": [
                        {
                            "symbol": "TSLA",
                            "regularMarketPrice": 250.12,
                            "currency": "USD",
                            "regularMarketTime": 1700000000,
                            "regularMarketChange": 3.45,
                            "regularMarketChangePercent": 1.4,
                            "marketState": "REGULAR",
                        }
                    ]
                }
            },
        )
    )

    quote = await market.fetch_stock_quote("TSLA")

    assert route.called
    assert quote.symbol == "TSLA"
    assert quote.price == pytest.approx(250.12)
    assert quote.currency == "USD"
    assert quote.change == pytest.approx(3.45)
    assert quote.percent_change == pytest.approx(1.4)
    assert quote.market_state == "REGULAR"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_stock_quote_returns_fallback_on_invalid_payload() -> None:
    respx.get(market.YAHOO_QUOTE_URL).mock(return_value=Response(200, json={}))

    quote = await market.fetch_stock_quote("TSLA")

    assert quote.is_fallback


@pytest.mark.asyncio
@respx.mock
async def test_fetch_stock_quote_uses_fallback_when_network_unavailable() -> None:
    request = httpx.Request(
        "GET",
        market.YAHOO_QUOTE_URL,
        params={"symbols": "TSLA"},
        headers={"User-Agent": market.USER_AGENT},
    )
    respx.get(
        market.YAHOO_QUOTE_URL,
        params={"symbols": "TSLA"},
        headers={"User-Agent": market.USER_AGENT},
    ).mock(side_effect=httpx.ConnectTimeout("network unavailable", request=request))

    quote = await market.fetch_stock_quote("TSLA")

    assert quote.is_fallback
    assert quote.market_state == market.FALLBACK_MARKET_STATE
    assert quote.price == pytest.approx(market.FALLBACK_PRICE)
