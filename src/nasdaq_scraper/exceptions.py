"""Custom exception hierarchy for the Nasdaq scraping library."""


class ScrapingError(Exception):
    """Base error for all scraping-related failures."""


class ConnectionError(ScrapingError):
    """Raised when network operations fail or time out."""


class ElementNotFoundError(ScrapingError):
    """Raised when required HTML elements are missing."""


class ParsingError(ScrapingError):
    """Raised when extracted values cannot be parsed correctly."""
