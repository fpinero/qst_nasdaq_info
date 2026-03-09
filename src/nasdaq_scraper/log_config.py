"""Logging utilities for the Nasdaq scraper package."""

import logging

LOGGER_NAME = "nasdaq_scraper"


def configure_library_logger(level: int = logging.INFO) -> logging.Logger:
    """Configure and return the package logger.

    The logger is initialized only once to avoid duplicate handlers when the
    library is imported in larger applications.
    """
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        logger.setLevel(level)
        return logger

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


def get_logger() -> logging.Logger:
    """Return the package logger without mutating configuration."""
    return logging.getLogger(LOGGER_NAME)
