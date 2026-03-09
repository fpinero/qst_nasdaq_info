# Workflow standards

This document defines branch, commit, and pull request conventions for this repository.

## Branch naming

- Use short-lived branches.
- Prefix by intent:
  - `feature/<scope>` for new behavior.
  - `fix/<scope>` for bug fixes.
- Keep one atomic task per branch whenever possible.

Examples:

- `feature/extract-price`
- `feature/hito-4-etf-extraction`
- `fix/playwright-firefox-fallback`

## Commit message template

Write commit messages in English using conventional prefixes:

- `feat: ...`
- `fix: ...`
- `docs: ...`
- `test: ...`
- `chore: ...`

Guidelines:

- First line describes the intent in imperative style.
- Optional body explains why the change exists.
- Keep each commit focused and reviewable.

## Pull request quality rules

- Scope each PR to one task or tightly related set of changes.
- Include verification evidence (commands run and outcomes).
- Avoid mixing unrelated refactors with feature or bug changes.
- Ensure quality gates are green before merge:
  - `ruff check`
  - `mypy`
  - `pytest`

## Default delivery flow

1. Create `feature/*` or `fix/*` branch from `main`.
2. Implement one milestone slice.
3. Run tests and quality gates.
4. Open PR with concise summary and validation evidence.
5. Merge to `main` using merge commit.
