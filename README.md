# qst_nasdaq_info

Python library that scrapes Nasdaq stock pages for a ticker and returns quote plus ETF holdings data as a JSON-compatible dictionary.

## Features

- Fetches `price`, `change`, and `change_percent` from Nasdaq quote data.
- Extracts ETF rows from the two Top-10 holding tables.
- Applies anti-blocking transport behavior (header rotation, retries, backoff, block detection).
- Uses browser hydration fallback for dynamic ETF tables.
- Exposes a simple public API: `get_ticker_data(ticker)`.

## Installation

### Base library

```bash
pip install qst-nasdaq-info
```

### Local development install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,browser]"
```

## Playwright browser setup

ETF tables are often rendered dynamically, so browser support is strongly recommended.

```bash
python -m playwright install chromium firefox
```

## Usage

```python
import json
import nasdaq_scraper

data = nasdaq_scraper.get_ticker_data("baba")
print(json.dumps(data, indent=2))
```

Expected output shape:

```json
{
  "ticker": "baba",
  "price": 131.26,
  "change": 0.47,
  "change_percent": 0.36,
  "etfs": [
    {
      "symbol": "FDNI",
      "name": "First Trust Dow Jones International Internet ETF",
      "weighting": 9.91
    }
  ]
}
```

## Public API and errors

Main function:

- `nasdaq_scraper.get_ticker_data(ticker: str) -> dict`

Raised errors:

- `ParsingError`: invalid ticker format or malformed numeric values.
- `ElementNotFoundError`: required fields missing in Nasdaq payloads.
- `ConnectionError`: network or browser fetch failures.

## Caching policy

This library does not implement internal caching. It always fetches fresh data. Cache handling belongs to the parent application.

## Dependency source of truth

Dependencies are managed in `pyproject.toml`. No separate `requirements.txt` is maintained to avoid duplicate dependency declarations.

## Troubleshooting

- **ETF list is empty**: install browser extras and run `python -m playwright install chromium firefox`.
- **Chromium fails to load Nasdaq**: the transport already attempts Firefox fallback automatically.
- **Integration tests are skipped**: run with `RUN_LIVE_TESTS=1`.
