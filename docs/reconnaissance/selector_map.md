# Selector map for Nasdaq ticker pages

This file documents selector candidates validated during milestone 1 reconnaissance.

## Price block

- Primary container candidate: `div.nsdq-quote-header[data-symbol]`
- Component wrapper candidate: `div.nsdq-quote-header__info-wrapper`
- Web component candidate: `nsdq-quote-header`

Note: static HTML currently exposes skeleton placeholders and the quote web component shell, not a fully rendered numeric price payload.

## API mapping for quote fields

- Endpoint: `GET https://api.nasdaq.com/api/quote/{SYMBOL}/info?assetclass=stocks`
- Path for `price`: `data.primaryData.lastSalePrice`
- Path for `change`: `data.primaryData.netChange`
- Path for `change_percent`: `data.primaryData.percentageChange`

## ETF table heading candidates

- Heading text 1: `Nasdaq Listed ETFs where {TICKER} is a top 10 holding`
- Heading text 2: `ETFs with {TICKER} as a Top 10 Holding`

## ETF table structure candidates

- Section scoped by heading text: `section:has(h2,h3,h4)`
- Table element: `table`
- Rows: `tr`
- Cells: `td`

Note: current static HTML for tested tickers (`baba`, `aapl`, `msft`) does not include these headings directly, so ETF extraction requires dynamic network discovery and runtime fallback logic.
