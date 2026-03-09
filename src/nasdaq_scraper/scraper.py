"""Public scraping entrypoint and quote extraction flow."""

from __future__ import annotations

import json
import math
import re
from typing import Any

from nasdaq_scraper.exceptions import ElementNotFoundError, ParsingError
from nasdaq_scraper.parsing import parse_change, parse_money, parse_percent
from nasdaq_scraper.transport import NasdaqHttpClient, TransportConfig
from nasdaq_scraper.types import TickerData

_TICKER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9.-]{0,9}$")


def get_ticker_data(ticker: str, *, transport_config: TransportConfig | None = None) -> TickerData:
    """Scrape Nasdaq quote data for one ticker.

    Returns quote metrics with an ETF list placeholder while ETF extraction is
    implemented in subsequent milestones.
    """
    normalized_ticker = _normalize_ticker(ticker)
    ticker_upper = normalized_ticker.upper()

    client = NasdaqHttpClient(config=transport_config)
    payload = _fetch_quote_info_payload(client=client, ticker=ticker_upper)

    primary_data = payload.get("primaryData")
    if not isinstance(primary_data, dict):
        raise ElementNotFoundError("Missing 'primaryData' object in quote payload")

    price_raw = _require_str(primary_data, "lastSalePrice")
    change_raw = _require_str(primary_data, "netChange")
    change_percent_raw = _require_str(primary_data, "percentageChange")

    price = parse_money(price_raw)
    change = parse_change(change_raw)
    change_percent = parse_percent(change_percent_raw)

    _validate_quote_values(price=price, change=change, change_percent=change_percent)

    return {
        "ticker": normalized_ticker,
        "price": price,
        "change": change,
        "change_percent": change_percent,
        "etfs": [],
    }


def _normalize_ticker(ticker: str) -> str:
    """Normalize ticker and enforce supported characters."""
    normalized = ticker.strip().lower()
    if not normalized:
        raise ParsingError("Ticker must not be empty")
    if _TICKER_RE.fullmatch(normalized) is None:
        raise ParsingError(f"Ticker has unsupported format: {ticker!r}")
    return normalized


def _fetch_quote_info_payload(client: NasdaqHttpClient, ticker: str) -> dict[str, Any]:
    """Fetch and decode quote info payload from Nasdaq API."""
    url = f"https://api.nasdaq.com/api/quote/{ticker}/info?assetclass=STOCKS"
    response = client.get(
        url,
        extra_headers={
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.nasdaq.com",
            "Referer": f"https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}",
        },
    )

    try:
        decoded = json.loads(response.body)
    except json.JSONDecodeError as error:
        raise ParsingError("Quote API response is not valid JSON") from error

    data = decoded.get("data")
    if not isinstance(data, dict):
        raise ElementNotFoundError("Missing 'data' object in quote API response")
    return data


def _require_str(payload: dict[str, Any], field_name: str) -> str:
    """Read required string field from payload."""
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ElementNotFoundError(f"Missing required quote field '{field_name}'")
    return value


def _validate_quote_values(*, price: float, change: float, change_percent: float) -> None:
    """Validate parsed quote numbers are finite and usable."""
    values = {
        "price": price,
        "change": change,
        "change_percent": change_percent,
    }
    for key, value in values.items():
        if not math.isfinite(value):
            raise ParsingError(f"Parsed '{key}' is not finite: {value!r}")
