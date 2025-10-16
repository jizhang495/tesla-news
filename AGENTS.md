# Repository Guidelines

## Project Structure & Module Organization
This repository is intentionally empty so contributors can layer on features without legacy baggage. Keep all runtime code inside `src/`, grouping modules by domain (`src/api`, `src/cli`, etc.) and expose a single package initializer. Mirror that structure in `tests/` so every module ships with a peer test module. Place scripts that wire up local tooling in `scripts/`, and keep large assets or fixtures under `assets/`. Configuration files (`pyproject.toml`, `.env.example`, CI manifests) live at the repository root so they are easy to discover.

## Build, Test, and Development Commands
Bootstrap dependencies with `make install` (expected to create or update a local virtual environment) and format the codebase with `make format`, which should call `ruff --fix` and `black`. Run static analysis through `make lint`, combining `ruff` and any type checker you introduce. Execute your full test suite via `make test`, and prefer chaining everything together with `make check` before pushing. Document any additional task runners (for example, Poetry or Hatch) directly in the Makefile so the command surface stays consistent.

## Coding Style & Naming Conventions
Target Python 3.11 and adhere to PEP 8 with four-space indents. Name modules and functions in `snake_case`, classes in `PascalCase`, and constants in `UPPER_SNAKE_CASE`. Favor explicit imports over star imports, and keep public APIs small by exporting through `__all__`. Run `ruff` and `black` prior to committing to ensure formatting stays deterministic.

## Testing Guidelines
Write tests with `pytest`, placing fixtures in `tests/conftest.py` or `tests/fixtures/`. Name test files `test_<module>.py` and individual tests `test_<behavior>`. All new features must include unit coverage and, when applicable, integration cases under `tests/integration/`. Target at least 90% line coverage; validate locally with `pytest --cov=src --cov-report=term-missing`. When reproducing a bug, first add a failing regression test, then implement the fix.

## Commit & Pull Request Guidelines
Although the history is empty today, start with Conventional Commits (`feat: add oauth client`, `fix(api): handle null ids`) so automated changelog tooling can be added later. Keep commits scoped to a single concern and describe the behavior change in the body. Pull requests should link to any tracking issue, summarize the approach, note testing performed (`make check`), and attach screenshots or CLI transcripts when updating user-facing flows. Request review once the CI pipeline is green and update this guide if your changes introduce new tooling or structure.
