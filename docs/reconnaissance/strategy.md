# Scraping strategy after reconnaissance

## Scope

This strategy is based on the milestone 1 reconnaissance script (`scripts/recon_nasdaq.py`) executed against:

- `https://www.nasdaq.com/es/market-activity/stocks/baba`
- `https://www.nasdaq.com/es/market-activity/stocks/aapl`
- `https://www.nasdaq.com/es/market-activity/stocks/msft`

## Observed facts

- Static HTML returns HTTP 200 and includes quote component shells and skeleton loaders.
- Numeric quote values are not present as plain static literals in tested pages.
- Embedded API settings include `https://qcapi.nasdaq.com/api` (403 when called directly) and `https://api.nasdaq.com/api/nordic`.
- Quote endpoints are reachable through `https://api.nasdaq.com/api/quote/{SYMBOL}/...`.
- For the tested pages, ETF heading text is not present in static HTML, which indicates dynamic rendering or deferred loading.

## Recommended extraction strategy

1. API-first for quote metrics.
2. HTML-assisted for structural checks and future fallback selectors.
3. Browser-assisted (Playwright) for ETF holdings discovery when static HTML and known API routes are insufficient.

## Implementation plan for next milestones

### Quote data (`price`, `change`, `change_percent`)

- Use `GET https://api.nasdaq.com/api/quote/{SYMBOL}/info?assetclass=stocks`.
- Parse:
  - `data.primaryData.lastSalePrice`
  - `data.primaryData.netChange`
  - `data.primaryData.percentageChange`
- Normalize numeric strings to float values.

### ETF data (`symbol`, `name`, `weighting`)

- First attempt: inspect static HTML by heading text candidates documented in `selector_map.md`.
- If tables are not found, run Playwright reconnaissance mode with network capture enabled and record XHR/Fetch calls triggered by quote page widgets.
- Promote discovered endpoint(s) to primary source for ETF rows.
- Keep HTML selector fallback to handle endpoint regressions.

Workaround implemented:

- Use Playwright-first extraction for ETF tables because the initial HTML often includes only skeleton rows.
- Wait explicitly for non-empty `.jupiter22-etf-stocks-holdings-bar-chart-table__symbol` nodes before parsing table rows.
- Keep static HTML fallback and return `etfs: []` safely if dynamic extraction cannot run.

## Anti-blocking posture to apply in hito 2

- Rotate User-Agent and full browser-like headers.
- Use retry with bounded exponential backoff and jitter.
- Detect and classify blocking patterns (403/429/challenge pages/empty payload anomalies).
- Keep respectful delays between calls.
- Reserve stealth browser mode for cases where API and static HTML are insufficient.

## Success criteria

- Quote extraction works consistently for `baba`, `aapl`, `msft`.
- ETF extraction either:
  - obtains rows from discovered endpoints, or
  - returns an empty list in controlled fashion when data is unavailable.
- Selector and endpoint definitions remain centralized and easy to update.
