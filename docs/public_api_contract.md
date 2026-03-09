# Public API contract

## Main entrypoint

- Function: `nasdaq_scraper.get_ticker_data(ticker: str) -> dict`
- Purpose: fetch fresh quote and ETF holdings data for a single ticker.
- Cache policy: no internal cache is used by this library.

## Output contract

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

## Error contract

- `ParsingError`
  - Trigger: invalid ticker format or malformed numeric values.
  - Action: validate input and inspect source payload formatting.

- `ElementNotFoundError`
  - Trigger: required fields are missing in Nasdaq responses.
  - Action: re-run reconnaissance and update selectors or payload paths.

- `ConnectionError`
  - Trigger: network failures, blocked endpoints, browser fetch failures.
  - Action: retry with backoff, verify connectivity, or use browser fallback dependencies.
