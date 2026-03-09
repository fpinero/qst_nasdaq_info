"""Type contracts for the Nasdaq scraper public output."""

from typing import TypedDict


class EtfEntry(TypedDict):
    """Normalized ETF item from Nasdaq tables."""

    symbol: str
    name: str
    weighting: float


class TickerData(TypedDict):
    """Top-level response returned by the scraper."""

    ticker: str
    price: float
    change: float
    change_percent: float
    etfs: list[EtfEntry]
