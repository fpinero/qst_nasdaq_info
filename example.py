"""Example usage for qst_nasdaq_info."""

from __future__ import annotations

import json

import nasdaq_scraper


def main() -> None:
    """Fetch and print Nasdaq data for a sample ticker."""
    data = nasdaq_scraper.get_ticker_data("baba")
    print(json.dumps(data, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
