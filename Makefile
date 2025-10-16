.PHONY: install format lint test run check export

install:
	uv sync --extra dev

format:
	uv run --extra dev ruff --fix src tests
	uv run --extra dev black src tests

lint:
	uv run --extra dev ruff src tests
	uv run --extra dev mypy src

test:
	uv run --extra dev pytest --cov=src --cov-report=term-missing

run:
	uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

check: format lint test

export:
	uv export --format requirements-txt --no-dev > requirements.txt
