VENV := .venv
PYTHON := $(VENV)/bin/python

.PHONY: install format lint test run check

install:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .[dev]

format:
	$(VENV)/bin/ruff --fix src tests
	$(VENV)/bin/black src tests

lint:
	$(VENV)/bin/ruff src tests
	$(VENV)/bin/mypy src

test:
	$(VENV)/bin/pytest --cov=src --cov-report=term-missing

run:
	$(VENV)/bin/uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

check: format lint test
