"""Reconnaissance helpers for Nasdaq scraping strategy validation."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import asdict
import json
import re
from typing import Any
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen

DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es-ES;q=0.8",
    "Referer": "https://www.nasdaq.com/",
}

API_HEADERS: dict[str, str] = {
    "User-Agent": DEFAULT_HEADERS["User-Agent"],
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.nasdaq.com",
    "Referer": "https://www.nasdaq.com/",
}


@dataclass(slots=True)
class ApiProbe:
    """Represents the result of probing one API endpoint."""

    endpoint_name: str
    url: str
    status_code: int
    ok: bool
    json_detected: bool
    data_keys: list[str]
    message: str


@dataclass(slots=True)
class TickerRecon:
    """Reconnaissance result for one ticker page."""

    ticker: str
    page_url: str
    page_status_code: int
    html_size: int
    has_quote_component: bool
    has_quote_skeleton: bool
    has_price_literal: bool
    has_etf_heading_in_html: bool
    api_settings_hosts: list[str]
    discovered_quote_endpoints: list[str]
    api_probes: list[ApiProbe]
    selector_candidates: dict[str, list[str]]

    def to_dict(self) -> dict[str, Any]:
        """Return serializable representation."""
        payload = asdict(self)
        payload["api_probes"] = [asdict(probe) for probe in self.api_probes]
        return payload


def fetch_text(url: str, headers: dict[str, str], timeout: int = 30) -> tuple[int, str]:
    """Fetch URL and return status code plus body text."""
    request = Request(url, headers=headers)
    with urlopen(request, timeout=timeout) as response:
        status_code = response.getcode() or 200
        body = response.read().decode("utf-8", "ignore")
    return status_code, body


def parse_query_params(raw_query: str) -> dict[str, str]:
    """Parse Nasdaq endpoint query params from settings format.

    Input format example: ``assetclass:STOCKS\r\nfromdate:2020-01-01``.
    """
    params: dict[str, str] = {}
    for line in raw_query.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", maxsplit=1)
        key = key.strip()
        value = value.strip()
        if key and value:
            params[key] = value
    return params


def extract_api_settings(html: str) -> dict[str, dict[str, Any]]:
    """Extract `*ApiSettings` JSON objects embedded in page HTML."""
    settings: dict[str, dict[str, Any]] = {}
    for match in re.finditer(r'"([A-Za-z0-9_]+ApiSettings)"\s*:\s*\{', html):
        key = match.group(1)
        object_start = html.find("{", match.start())
        if object_start == -1:
            continue

        brace_level = 0
        object_end = -1
        for index in range(object_start, len(html)):
            char = html[index]
            if char == "{":
                brace_level += 1
            elif char == "}":
                brace_level -= 1
                if brace_level == 0:
                    object_end = index
                    break

        if object_end == -1:
            continue

        snippet = html[object_start : object_end + 1]
        try:
            settings[key] = json.loads(snippet)
        except json.JSONDecodeError:
            continue
    return settings


def build_quote_probe_urls(settings: dict[str, dict[str, Any]], ticker: str) -> list[tuple[str, str]]:
    """Build candidate quote endpoint URLs from embedded settings."""
    urls: list[tuple[str, str]] = []
    normalized_symbol = ticker.upper()

    for payload in settings.values():
        host = str(payload.get("remoteHost", "")).rstrip("/")
        quote_endpoints = payload.get("endpoints", {}).get("quote", {})
        if not host or not isinstance(quote_endpoints, dict):
            continue

        for endpoint_name in ("info", "summary"):
            endpoint = quote_endpoints.get(endpoint_name)
            if not isinstance(endpoint, dict):
                continue

            endpoint_url = str(endpoint.get("endpointUrl", "")).replace("{symbol}", normalized_symbol)
            if not endpoint_url:
                continue

            params = parse_query_params(str(endpoint.get("queryParams", "")))
            query_string = urlencode(params)
            full_url = f"{host}{endpoint_url}"
            if query_string:
                full_url = f"{full_url}?{query_string}"

            urls.append((endpoint_name, full_url))

            if "qcapi.nasdaq.com" in full_url:
                urls.append((endpoint_name, full_url.replace("qcapi.nasdaq.com", "api.nasdaq.com")))
    return dedupe_probes(urls)


def dedupe_probes(items: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Deduplicate endpoint probes preserving insertion order."""
    seen: set[tuple[str, str]] = set()
    unique: list[tuple[str, str]] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


def probe_api(endpoint_name: str, url: str) -> ApiProbe:
    """Probe a JSON endpoint and summarize response shape."""
    try:
        status_code, body = fetch_text(url, headers=API_HEADERS)
    except HTTPError as error:
        return ApiProbe(
            endpoint_name=endpoint_name,
            url=url,
            status_code=error.code,
            ok=False,
            json_detected=False,
            data_keys=[],
            message=f"HTTP {error.code}",
        )
    except URLError as error:
        return ApiProbe(
            endpoint_name=endpoint_name,
            url=url,
            status_code=0,
            ok=False,
            json_detected=False,
            data_keys=[],
            message=f"URL error: {error.reason}",
        )

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return ApiProbe(
            endpoint_name=endpoint_name,
            url=url,
            status_code=status_code,
            ok=False,
            json_detected=False,
            data_keys=[],
            message="Non-JSON response",
        )

    data = payload.get("data")
    data_keys = list(data.keys()) if isinstance(data, dict) else []
    status_payload = payload.get("status")
    status_message = "JSON response"
    if isinstance(status_payload, dict):
        status_message = f"JSON response, rCode={status_payload.get('rCode')}"

    return ApiProbe(
        endpoint_name=endpoint_name,
        url=url,
        status_code=status_code,
        ok=200 <= status_code < 300,
        json_detected=True,
        data_keys=data_keys,
        message=status_message,
    )


def detect_etf_heading_in_html(html: str, ticker: str) -> bool:
    """Return whether ETF heading text appears directly in static HTML."""
    normalized = html.lower()
    ticker_upper = ticker.upper()
    candidates = (
        f"nasdaq listed etfs where {ticker_upper.lower()} is a top 10 holding",
        f"etfs with {ticker_upper.lower()} as a top 10 holding",
        "100 day price change",
    )
    return any(candidate in normalized for candidate in candidates)


def selector_candidates() -> dict[str, list[str]]:
    """Return candidate selectors and fallback extraction paths."""
    return {
        "quote_container": [
            "div.nsdq-quote-header[data-symbol]",
            "div.nsdq-quote-header__info-wrapper",
            "nsdq-quote-header",
        ],
        "quote_fallback_api": [
            "GET https://api.nasdaq.com/api/quote/{SYMBOL}/info?assetclass=stocks",
            "data.primaryData.lastSalePrice -> price",
            "data.primaryData.netChange -> change",
            "data.primaryData.percentageChange -> change_percent",
        ],
        "etf_table_heading_text": [
            "Nasdaq Listed ETFs where {TICKER} is a top 10 holding",
            "ETFs with {TICKER} as a Top 10 Holding",
        ],
        "etf_table_candidate_selectors": [
            "section:has(h2,h3,h4)",
            "table",
            "tr",
            "td",
        ],
    }


def run_recon_for_ticker(ticker: str, language: str = "es") -> TickerRecon:
    """Execute reconnaissance flow for one Nasdaq ticker page."""
    page_url = f"https://www.nasdaq.com/{language}/market-activity/stocks/{ticker.lower()}"
    page_status_code, html = fetch_text(page_url, headers=DEFAULT_HEADERS)

    api_settings = extract_api_settings(html)
    probes: list[ApiProbe] = []
    for endpoint_name, url in build_quote_probe_urls(api_settings, ticker=ticker):
        probes.append(probe_api(endpoint_name=endpoint_name, url=url))

    discovered_quote_endpoints = sorted(
        {
            probe.url
            for probe in probes
            if probe.ok and probe.json_detected and probe.endpoint_name in {"info", "summary"}
        }
    )

    return TickerRecon(
        ticker=ticker.lower(),
        page_url=page_url,
        page_status_code=page_status_code,
        html_size=len(html),
        has_quote_component="<nsdq-quote-header" in html.lower(),
        has_quote_skeleton="nsdq-quote-header-skeleton" in html.lower(),
        has_price_literal=bool(re.search(r"\$\s?\d{1,4}\.\d{2}", html)),
        has_etf_heading_in_html=detect_etf_heading_in_html(html=html, ticker=ticker),
        api_settings_hosts=sorted(
            {
                str(payload.get("remoteHost", "")).replace("\\/", "/")
                for payload in api_settings.values()
                if isinstance(payload, dict) and payload.get("remoteHost")
            }
        ),
        discovered_quote_endpoints=discovered_quote_endpoints,
        api_probes=probes,
        selector_candidates=selector_candidates(),
    )
