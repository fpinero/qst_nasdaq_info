"""HTTP and browser transport layer with anti-blocking safeguards."""

from __future__ import annotations

from dataclasses import dataclass
import gzip
import importlib
import random
import time
from typing import Mapping, cast
import zlib
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.request import Request
from urllib.request import urlopen

from nasdaq_scraper.exceptions import ConnectionError
from nasdaq_scraper.log_config import get_logger

DEFAULT_USER_AGENTS: tuple[str, ...] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
)

DEFAULT_ACCEPT_LANGUAGES: tuple[str, ...] = (
    "en-US,en;q=0.9",
    "es-ES,es;q=0.9,en-US;q=0.8",
    "en-GB,en;q=0.9,en-US;q=0.8",
)

DEFAULT_VIEWPORTS: tuple[tuple[int, int], ...] = (
    (1366, 768),
    (1440, 900),
    (1536, 864),
    (1920, 1080),
)

DEFAULT_TIMEZONES: tuple[str, ...] = (
    "America/New_York",
    "America/Chicago",
    "Europe/Madrid",
)

DEFAULT_LOCALES: tuple[str, ...] = (
    "en-US",
    "es-ES",
)


@dataclass(slots=True)
class TransportConfig:
    """Configurable transport behavior for anti-blocking and resiliency."""

    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_backoff_base_seconds: float = 0.8
    retry_backoff_max_seconds: float = 8.0
    retry_jitter_seconds: float = 0.25
    polite_delay_min_seconds: float = 0.35
    polite_delay_max_seconds: float = 1.25
    user_agents: tuple[str, ...] = DEFAULT_USER_AGENTS
    accept_languages: tuple[str, ...] = DEFAULT_ACCEPT_LANGUAGES
    browser_locales: tuple[str, ...] = DEFAULT_LOCALES
    browser_timezones: tuple[str, ...] = DEFAULT_TIMEZONES
    browser_viewports: tuple[tuple[int, int], ...] = DEFAULT_VIEWPORTS
    blocked_status_codes: tuple[int, ...] = (403, 429)
    blocked_body_markers: tuple[str, ...] = (
        "access denied",
        "cloudflare",
        "captcha",
        "forbidden",
        "unusual traffic",
    )


@dataclass(slots=True)
class HttpResponse:
    """Represents one HTTP response returned by transport layer."""

    url: str
    status_code: int
    body: str
    headers: dict[str, str]


@dataclass(slots=True)
class BlockDetection:
    """Result of block detection logic over HTTP response."""

    blocked: bool
    reason: str


class UserAgentRotator:
    """Randomly rotates user-agent values for outgoing requests."""

    def __init__(self, user_agents: tuple[str, ...], rng: random.Random | None = None) -> None:
        if not user_agents:
            raise ValueError("user_agents must not be empty")
        self._user_agents = user_agents
        self._rng = rng or random.Random()

    def next(self) -> str:
        """Return one user-agent string."""
        return self._rng.choice(self._user_agents)


def detect_blocking(status_code: int, body: str, config: TransportConfig) -> BlockDetection:
    """Detect anti-bot or blocked responses from status and body content."""
    if status_code in config.blocked_status_codes:
        return BlockDetection(blocked=True, reason=f"status code {status_code}")

    lowered_body = body.lower()
    for marker in config.blocked_body_markers:
        if marker in lowered_body:
            return BlockDetection(blocked=True, reason=f"body marker '{marker}'")

    return BlockDetection(blocked=False, reason="none")


def build_browser_headers(
    *,
    user_agent: str,
    accept_language: str,
    referer: str,
    extra_headers: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Build browser-like HTTP headers for requests."""
    headers: dict[str, str] = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": accept_language,
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": referer,
    }
    if extra_headers:
        headers.update(dict(extra_headers))
    return headers


class NasdaqHttpClient:
    """HTTP client with anti-blocking and retry behavior."""

    def __init__(self, config: TransportConfig | None = None, rng: random.Random | None = None) -> None:
        self.config = config or TransportConfig()
        self._rng = rng or random.Random()
        self._ua_rotator = UserAgentRotator(self.config.user_agents, rng=self._rng)
        self._logger = get_logger()

    def get(self, url: str, extra_headers: Mapping[str, str] | None = None) -> HttpResponse:
        """Fetch URL with retries, rotating identifiers, and block detection."""
        attempts = self.config.max_retries + 1
        last_error: str | None = None

        for attempt in range(1, attempts + 1):
            self._sleep_polite_delay()
            user_agent = self._ua_rotator.next()
            accept_language = self._rng.choice(self.config.accept_languages)
            headers = build_browser_headers(
                user_agent=user_agent,
                accept_language=accept_language,
                referer="https://www.nasdaq.com/",
                extra_headers=extra_headers,
            )

            try:
                response = self._send(url=url, headers=headers)
            except ConnectionError as error:
                last_error = str(error)
                self._logger.warning("HTTP transport error on attempt %s/%s: %s", attempt, attempts, error)
                if attempt < attempts:
                    self._sleep_retry_backoff(attempt)
                continue

            detection = detect_blocking(
                status_code=response.status_code,
                body=response.body,
                config=self.config,
            )
            if detection.blocked:
                last_error = f"blocked response ({detection.reason})"
                self._logger.warning(
                    "Blocked response on attempt %s/%s for %s: %s",
                    attempt,
                    attempts,
                    url,
                    detection.reason,
                )
                if attempt < attempts:
                    self._sleep_retry_backoff(attempt)
                    continue
                raise ConnectionError(last_error)

            return response

        raise ConnectionError(last_error or "failed to fetch URL")

    def _send(self, url: str, headers: Mapping[str, str]) -> HttpResponse:
        """Send one request and return response payload."""
        request = Request(url, headers=dict(headers))
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as raw_response:
                status_code = raw_response.getcode() or 200
                raw_body = raw_response.read()
                content_encoding = str(raw_response.headers.get("Content-Encoding", "")).lower()
                body = self._decode_body(raw_body=raw_body, content_encoding=content_encoding)
                response_headers = dict(raw_response.headers.items())
        except HTTPError as error:
            response_body = error.read().decode("utf-8", "ignore")
            raise ConnectionError(f"HTTPError {error.code} for {url}: {response_body[:200]}") from error
        except URLError as error:
            raise ConnectionError(f"URLError for {url}: {error.reason}") from error
        except TimeoutError as error:
            raise ConnectionError(f"Timeout for {url}") from error

        return HttpResponse(url=url, status_code=status_code, body=body, headers=response_headers)

    def _decode_body(self, raw_body: bytes, content_encoding: str) -> str:
        """Decode response bytes handling common content encodings."""
        decoded = raw_body

        if "gzip" in content_encoding:
            decoded = gzip.decompress(raw_body)
        elif "deflate" in content_encoding:
            decoded = zlib.decompress(raw_body)
        elif "br" in content_encoding:
            try:
                brotli_module = importlib.import_module("brotli")
                decoded = brotli_module.decompress(raw_body)
            except ModuleNotFoundError:
                decoded = raw_body

        return decoded.decode("utf-8", "ignore")

    def _sleep_polite_delay(self) -> None:
        """Sleep random short delay before each request."""
        sleep_time = self._rng.uniform(
            self.config.polite_delay_min_seconds,
            self.config.polite_delay_max_seconds,
        )
        time.sleep(sleep_time)

    def _sleep_retry_backoff(self, attempt: int) -> None:
        """Sleep retry backoff with bounded exponential strategy plus jitter."""
        base = self.config.retry_backoff_base_seconds * (2 ** (attempt - 1))
        bounded = min(base, self.config.retry_backoff_max_seconds)
        jitter = self._rng.uniform(0.0, self.config.retry_jitter_seconds)
        time.sleep(bounded + jitter)


def fetch_with_playwright_fallback(
    url: str,
    config: TransportConfig | None = None,
    *,
    wait_for_selector: str = "body",
    wait_timeout_ms: int = 15000,
    wait_for_etf_rows: bool = False,
) -> str:
    """Fetch page HTML using Playwright with rotating browser identifiers.

    This function is optional and requires `playwright`. If `playwright-stealth`
    is installed, it applies stealth hardening automatically.
    """
    runtime_config = config or TransportConfig()
    rng = random.Random()
    viewport_width, viewport_height = rng.choice(runtime_config.browser_viewports)
    locale = rng.choice(runtime_config.browser_locales)
    timezone = rng.choice(runtime_config.browser_timezones)
    user_agent = rng.choice(runtime_config.user_agents)

    try:
        playwright_module = importlib.import_module("playwright.sync_api")
        sync_playwright = playwright_module.sync_playwright
    except ModuleNotFoundError as error:
        raise ConnectionError(
            "Playwright fallback requested but playwright is not installed. "
            "Install optional dependency: pip install 'qst-nasdaq-info[browser]'"
        ) from error

    stealth_apply = None
    try:
        stealth_module = importlib.import_module("playwright_stealth")
        legacy = getattr(stealth_module, "stealth_sync", None)
        if callable(legacy):
            stealth_apply = legacy
        else:
            stealth_class = getattr(stealth_module, "Stealth", None)
            if stealth_class is not None:
                stealth_instance = stealth_class()
                stealth_apply = getattr(stealth_instance, "apply_stealth_sync", None)
    except ModuleNotFoundError:
        stealth_apply = None

    browser_errors: list[str] = []
    with sync_playwright() as playwright:
        for browser_name in ("chromium", "firefox"):
            browser_engine = getattr(playwright, browser_name)
            browser = None
            context = None
            try:
                browser = browser_engine.launch(headless=True)
                context = browser.new_context(
                    user_agent=user_agent,
                    locale=locale,
                    timezone_id=timezone,
                    viewport={"width": viewport_width, "height": viewport_height},
                    screen={"width": viewport_width, "height": viewport_height},
                )
                page = context.new_page()
                if callable(stealth_apply):
                    stealth_apply(page)

                page.goto(url, wait_until="domcontentloaded", timeout=wait_timeout_ms)
                page.wait_for_selector(wait_for_selector, timeout=wait_timeout_ms)

                if wait_for_etf_rows:
                    page.wait_for_selector(
                        ".jupiter22-etf-stocks-holdings-bar-chart-table",
                        timeout=wait_timeout_ms,
                    )
                    page.locator(
                        ".jupiter22-etf-stocks-holdings-bar-chart-table"
                    ).first.scroll_into_view_if_needed()
                    page.wait_for_function(
                        """
                        () => {
                            const symbols = Array.from(
                                document.querySelectorAll(
                                    '.jupiter22-etf-stocks-holdings-bar-chart-table__symbol'
                                )
                            );
                            return symbols.some((element) => {
                                const value = element.textContent || '';
                                return value.trim().length > 0;
                            });
                        }
                        """,
                        timeout=wait_timeout_ms,
                    )

                page.wait_for_load_state("networkidle", timeout=wait_timeout_ms)
                html = cast(str, page.content())

                context.close()
                browser.close()
                return html
            except Exception as error:  # pragma: no cover - depends on optional runtime tooling
                browser_errors.append(f"{browser_name}: {error}")
                try:
                    if context is not None:
                        context.close()
                except Exception:
                    pass
                try:
                    if browser is not None:
                        browser.close()
                except Exception:
                    pass

    joined_errors = " | ".join(browser_errors) or "unknown Playwright error"
    raise ConnectionError(f"Playwright fallback failed for {url}: {joined_errors}")

    # Unreachable, kept for type checkers.
    return ""
