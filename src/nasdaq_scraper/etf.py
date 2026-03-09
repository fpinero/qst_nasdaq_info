"""ETF table extraction utilities for Nasdaq stock pages."""

from __future__ import annotations

import html as html_lib
import re

from nasdaq_scraper.parsing import parse_percent
from nasdaq_scraper.types import EtfEntry

_BLOCK_PATTERN = re.compile(
    r'<div class="jupiter22-etf-stocks-holdings-bar-chart-table__(?:related_etfs|nasdaq_etfs)"'
    r"[\s\S]*?"
    r"<table class=\"jupiter22-etf-stocks-holdings-bar-chart-table__table\"[\s\S]*?</table>",
    flags=re.IGNORECASE,
)

_ROW_PATTERN = re.compile(
    r'<tr[^>]*class="[^"]*jupiter22-etf-stocks-holdings-bar-chart-table__row[^"]*"[^>]*>[\s\S]*?</tr>',
    flags=re.IGNORECASE,
)

_SYMBOL_PATTERN = re.compile(
    r'jupiter22-etf-stocks-holdings-bar-chart-table__symbol">\s*([^<\s][^<]*)\s*<',
    flags=re.IGNORECASE,
)

_NAME_PATTERN = re.compile(
    r'jupiter22-etf-stocks-holdings-bar-chart-table__company-name">\s*([^<\s][^<]*)\s*<',
    flags=re.IGNORECASE,
)

_WEIGHTAGE_CELL_PATTERN = re.compile(
    r'<td[^>]*class="[^"]*jupiter22-etf-stocks-holdings-bar-chart-table__row-data[^"]*"[^>]*>'
    r"(?P<body>[\s\S]*?)"
    r"</td>",
    flags=re.IGNORECASE,
)

_WEIGHTAGE_BODY_MARKER = "jupiter22-etf-stocks-holdings-bar-chart-table__weightage"

_PERCENT_PATTERN = re.compile(r"[+-]?\d+(?:\.\d+)?%")


def extract_etfs_from_html(html: str, ticker: str) -> list[EtfEntry]:
    """Extract and merge ETF rows from both Nasdaq holdings tables.

    The page includes two related tables in the same component. One table may
    include a 100-day price-change column that is ignored.
    """
    table_blocks = _extract_table_blocks(html=html)
    merged_rows: list[EtfEntry] = []

    for block in table_blocks:
        merged_rows.extend(_extract_rows_from_block(block))

    return _dedupe_etfs(merged_rows)


def _extract_table_blocks(html: str) -> list[str]:
    """Locate ETF table sections by heading markers and class-based fallback."""
    return [match.group(0) for match in _BLOCK_PATTERN.finditer(html)]


def _extract_rows_from_block(block_html: str) -> list[EtfEntry]:
    """Extract rows from one ETF section block."""
    rows: list[EtfEntry] = []
    for row_html in _ROW_PATTERN.findall(block_html):
        symbol = _extract_symbol(row_html)
        name = _extract_name(row_html)
        weighting = _extract_weighting(row_html)
        if symbol and name and weighting is not None:
            rows.append(
                {
                    "symbol": symbol,
                    "name": name,
                    "weighting": weighting,
                }
            )
    return rows


def _extract_symbol(row_html: str) -> str | None:
    """Extract ETF symbol from one row."""
    match = _SYMBOL_PATTERN.search(row_html)
    if match is None:
        return None
    symbol = _clean_text(match.group(1)).upper()
    return symbol or None


def _extract_name(row_html: str) -> str | None:
    """Extract ETF name from one row."""
    match = _NAME_PATTERN.search(row_html)
    if match is None:
        return None
    name = _clean_text(match.group(1))
    return name or None


def _extract_weighting(row_html: str) -> float | None:
    """Extract weighting percentage from one row."""
    cells = [match.group("body") for match in _WEIGHTAGE_CELL_PATTERN.finditer(row_html)]

    for cell_body in cells:
        if _WEIGHTAGE_BODY_MARKER not in cell_body.lower():
            continue

        percent_matches = _PERCENT_PATTERN.findall(cell_body)
        if not percent_matches:
            continue

        try:
            return parse_percent(percent_matches[-1])
        except (TypeError, ValueError):
            continue

    for cell_body in reversed(cells):
        if "price-change" in cell_body.lower():
            continue

        percent_matches = _PERCENT_PATTERN.findall(cell_body)
        if not percent_matches:
            continue

        try:
            return parse_percent(percent_matches[-1])
        except (TypeError, ValueError):
            continue

    return None


def _dedupe_etfs(rows: list[EtfEntry]) -> list[EtfEntry]:
    """Deduplicate ETF rows preserving original order."""
    deduped: list[EtfEntry] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row["symbol"], row["name"].lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def _clean_text(value: str) -> str:
    """Normalize whitespace and strip text."""
    normalized = " ".join(value.split()).strip()
    return html_lib.unescape(normalized)
