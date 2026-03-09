"""Online integration tests for public scraper API."""

from __future__ import annotations

import os

import pytest

import nasdaq_scraper


_RUN_LIVE = os.getenv("RUN_LIVE_TESTS", "0") == "1"


@pytest.mark.integration
@pytest.mark.skipif(not _RUN_LIVE, reason="Set RUN_LIVE_TESTS=1 to run online integration tests")
@pytest.mark.parametrize("ticker", ["baba", "aapl", "msft"])
def test_get_ticker_data_live_tickers(ticker: str) -> None:
    """Public API should return stable structure for known live tickers."""
    data = nasdaq_scraper.get_ticker_data(ticker)

    assert data["ticker"] == ticker
    assert isinstance(data["price"], float)
    assert isinstance(data["change"], float)
    assert isinstance(data["change_percent"], float)
    assert isinstance(data["etfs"], list)

    for row in data["etfs"]:
        assert isinstance(row["symbol"], str) and row["symbol"]
        assert isinstance(row["name"], str) and row["name"]
        assert isinstance(row["weighting"], float)


@pytest.mark.integration
@pytest.mark.skipif(not _RUN_LIVE, reason="Set RUN_LIVE_TESTS=1 to run online integration tests")
def test_no_etf_case_returns_empty_list() -> None:
    """Scraper should return a list type for ETFs even if empty."""
    # Ticker varies over time, this test validates contract shape only.
    data = nasdaq_scraper.get_ticker_data("ibm")
    assert isinstance(data["etfs"], list)
