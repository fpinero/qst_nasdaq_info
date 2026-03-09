"""Public package surface for the Nasdaq scraper library."""

from nasdaq_scraper.exceptions import ConnectionError, ElementNotFoundError, ParsingError, ScrapingError
from nasdaq_scraper.log_config import configure_library_logger, get_logger
from nasdaq_scraper.parsing import parse_change, parse_money, parse_percent
from nasdaq_scraper.recon import run_recon_for_ticker
from nasdaq_scraper.scraper import get_ticker_data
from nasdaq_scraper.transport import NasdaqHttpClient, TransportConfig, fetch_with_playwright_fallback
from nasdaq_scraper.types import EtfEntry, TickerData

__all__ = [
    "ConnectionError",
    "ElementNotFoundError",
    "EtfEntry",
    "NasdaqHttpClient",
    "ParsingError",
    "ScrapingError",
    "TickerData",
    "TransportConfig",
    "configure_library_logger",
    "fetch_with_playwright_fallback",
    "get_ticker_data",
    "get_logger",
    "parse_change",
    "parse_money",
    "parse_percent",
    "run_recon_for_ticker",
]
