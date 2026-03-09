"""Unit tests for ETF table extraction."""

from pathlib import Path

from nasdaq_scraper.etf import extract_etfs_from_html


def test_extract_etfs_from_hydrated_tables() -> None:
    """Extractor should parse both table variants and deduplicate rows."""
    fixture_path = Path(__file__).resolve().parents[1] / "fixtures" / "etf_tables_hydrated.html"
    html = fixture_path.read_text(encoding="utf-8")

    rows = extract_etfs_from_html(html, ticker="baba")

    assert rows == [
        {"symbol": "FDNI", "name": "First Trust ETF", "weighting": 9.91},
        {"symbol": "PGJ", "name": "Invesco ETF", "weighting": 7.66},
        {"symbol": "IDVO", "name": "Amplify ETF", "weighting": 4.0},
    ]


def test_extract_etfs_returns_empty_without_rows() -> None:
    """Extractor should return empty list when table rows are unavailable."""
    html = '<div class="jupiter22-etf-stocks-holdings-bar-chart-table__related_etfs"></div>'
    assert extract_etfs_from_html(html, ticker="baba") == []
