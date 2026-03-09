# Package architecture

This document defines the module conventions for `src/nasdaq_scraper/`.

## Module responsibilities

- `__init__.py`: public exports only.
- `types.py`: public type contracts (`TypedDict`) for output structures.
- `exceptions.py`: custom exception hierarchy for scraper failures.
- `log_config.py`: library logger setup and logger access helpers.
- `recon.py`: reconnaissance utilities to inspect rendering and discover API endpoints.
- `transport.py`: resilient HTTP and Playwright fallback transport with anti-blocking primitives.

## Naming conventions

- Public modules use descriptive names without abbreviations.
- Internal-only modules should use a leading underscore when introduced.
- Parsing and transport logic will be split into separate modules in upcoming milestones.

## Dependency boundaries

- Modules in this milestone stay dependency-light and import only standard library typing/logging features.
- Network and parsing dependencies are declared in `pyproject.toml`, but implementation modules that use them are added in later milestones.
