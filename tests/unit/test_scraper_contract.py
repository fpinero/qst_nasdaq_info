"""Unit tests for public scraper contract behavior."""

from __future__ import annotations

from typing import Any

import pytest

from nasdaq_scraper.exceptions import ParsingError
from nasdaq_scraper.scraper import get_ticker_data


class _FakeClient:
    """Simple fake transport client for scraper unit tests."""

    def __init__(self, body: str) -> None:
        self._body = body

    def get(self, url: str, extra_headers: dict[str, str] | None = None) -> Any:
        class _Resp:
            def __init__(self, payload: str) -> None:
                self.body = payload

        return _Resp(self._body)


def test_get_ticker_data_rejects_invalid_ticker() -> None:
    """Public API should validate ticker format before network usage."""
    with pytest.raises(ParsingError):
        get_ticker_data("$$$")
