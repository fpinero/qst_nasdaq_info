"""Unit tests for numeric parsing helpers."""

import pytest

from nasdaq_scraper.exceptions import ParsingError
from nasdaq_scraper.parsing import parse_change, parse_money, parse_percent


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("$131.26", 131.26),
        ("  USD 1,234.50 ", 1234.50),
        ("-0.18", -0.18),
    ],
)
def test_parse_money(raw: str, expected: float) -> None:
    """parse_money should normalize common money representations."""
    assert parse_money(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("+0.47", 0.47),
        ("-1.23", -1.23),
        ("Change: +4.00", 4.00),
    ],
)
def test_parse_change(raw: str, expected: float) -> None:
    """parse_change should support explicit sign and decorated strings."""
    assert parse_change(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("+0.36%", 0.36),
        ("-11.98%", -11.98),
        ("4%", 4.0),
    ],
)
def test_parse_percent(raw: str, expected: float) -> None:
    """parse_percent should return float without percent symbol."""
    assert parse_percent(raw) == expected


@pytest.mark.parametrize("raw", ["", "N/A", "--", "percent"])
def test_parsers_raise_for_invalid_input(raw: str) -> None:
    """Parsers should fail explicitly when numeric token is missing."""
    with pytest.raises(ParsingError):
        parse_money(raw)
