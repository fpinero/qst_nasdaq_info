"""Parsing helpers for quote numeric values."""

from __future__ import annotations

import re

from nasdaq_scraper.exceptions import ParsingError

_NUMBER_RE = re.compile(r"[+-]?\d+(?:,\d{3})*(?:\.\d+)?")


def _extract_number(value: str, *, field_name: str) -> float:
    """Extract a normalized float from a string containing one numeric token."""
    token_match = _NUMBER_RE.search(value)
    if token_match is None:
        raise ParsingError(f"Could not parse numeric value for '{field_name}': {value!r}")

    token = token_match.group(0).replace(",", "")
    try:
        return float(token)
    except ValueError as error:
        raise ParsingError(f"Invalid numeric token for '{field_name}': {token!r}") from error


def parse_money(value: str) -> float:
    """Parse money-like values such as `$130.61` into a float."""
    return _extract_number(value, field_name="price")


def parse_change(value: str) -> float:
    """Parse signed net change values such as `-0.18` or `+0.47`."""
    return _extract_number(value, field_name="change")


def parse_percent(value: str) -> float:
    """Parse percentage values such as `-0.14%` into a float without `%`."""
    return _extract_number(value, field_name="change_percent")
