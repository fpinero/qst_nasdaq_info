"""Unit tests for transport anti-blocking behavior."""

import random

import pytest

from nasdaq_scraper.exceptions import ConnectionError
from nasdaq_scraper.transport import HttpResponse, NasdaqHttpClient, TransportConfig, detect_blocking


def test_detect_blocking_by_status_code() -> None:
    """Blocking detector should flag configured HTTP blocked codes."""
    detection = detect_blocking(status_code=403, body="ok", config=TransportConfig())
    assert detection.blocked is True
    assert "403" in detection.reason


def test_detect_blocking_by_body_marker() -> None:
    """Blocking detector should flag anti-bot markers in response body."""
    detection = detect_blocking(
        status_code=200,
        body="Please complete CAPTCHA challenge",
        config=TransportConfig(),
    )
    assert detection.blocked is True


def test_http_client_retries_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    """HTTP client should retry transient failures and eventually return response."""
    config = TransportConfig(
        max_retries=2,
        polite_delay_min_seconds=0.0,
        polite_delay_max_seconds=0.0,
        retry_backoff_base_seconds=0.0,
        retry_backoff_max_seconds=0.0,
        retry_jitter_seconds=0.0,
    )
    client = NasdaqHttpClient(config=config, rng=random.Random(0))

    calls = {"count": 0}

    def fake_send(url: str, headers: dict[str, str]) -> HttpResponse:
        calls["count"] += 1
        if calls["count"] < 2:
            raise ConnectionError("temporary error")
        return HttpResponse(url=url, status_code=200, body="{}", headers={})

    monkeypatch.setattr(client, "_sleep_polite_delay", lambda: None)
    monkeypatch.setattr(client, "_sleep_retry_backoff", lambda attempt: None)
    monkeypatch.setattr(client, "_send", fake_send)

    response = client.get("https://example.com")

    assert response.status_code == 200
    assert calls["count"] == 2


def test_http_client_raises_when_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    """HTTP client should raise after blocked responses exhaust retries."""
    config = TransportConfig(
        max_retries=1,
        polite_delay_min_seconds=0.0,
        polite_delay_max_seconds=0.0,
        retry_backoff_base_seconds=0.0,
        retry_backoff_max_seconds=0.0,
        retry_jitter_seconds=0.0,
    )
    client = NasdaqHttpClient(config=config, rng=random.Random(0))

    monkeypatch.setattr(client, "_sleep_polite_delay", lambda: None)
    monkeypatch.setattr(client, "_sleep_retry_backoff", lambda attempt: None)
    monkeypatch.setattr(
        client,
        "_send",
        lambda url, headers: HttpResponse(url=url, status_code=429, body="rate limited", headers={}),
    )

    with pytest.raises(ConnectionError):
        client.get("https://example.com")
