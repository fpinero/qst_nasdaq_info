# Release checklist

Run this checklist before merging release-ready changes.

## Environment

- [ ] Virtual environment active.
- [ ] Dependencies installed from `pyproject.toml`.
- [ ] Playwright browsers installed if ETF extraction is required.

## Quality gates

- [ ] `python -m ruff check src tests`
- [ ] `python -m mypy src`
- [ ] `python -m pytest -m "not integration"`
- [ ] `RUN_LIVE_TESTS=1 python -m pytest tests/integration/test_live_tickers.py` (when network testing is needed)

## Functional checks

- [ ] `python example.py` runs successfully.
- [ ] `get_ticker_data("baba")` returns expected structure.
- [ ] ETF rows are non-empty when dynamic browser extraction works.

## Documentation

- [ ] `README.md` reflects current install and usage flow.
- [ ] Public API contract is up to date in `docs/public_api_contract.md`.
