# Detect Python command (python3, python, or py)
PYTHON := $(shell command -v python3 2> /dev/null || command -v python 2> /dev/null || command -v py 2> /dev/null || echo python3)

install:
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -e ".[dev]"

mongo-up:
	@echo "Starting MongoDB..."
	@docker compose up -d mongodb || echo "MongoDB already running or Docker not available"

mongo-down:
	@echo "Stopping MongoDB..."
	@docker compose stop mongodb || true

run: install mongo-up
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

up: install mongo-up
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info

down: mongo-down
	pkill -f "$(PYTHON) -m uvicorn app.main:app" || true

# Testing commands
test:
	$(PYTHON) -m pytest -v

test-unit:
	$(PYTHON) -m pytest tests/unit -v

test-coverage:
	$(PYTHON) -m pytest --cov=app --cov-report=html --cov-report=term-missing -v

test-coverage-xml:
	$(PYTHON) -m pytest --cov=app --cov-report=xml --cov-report=term-missing -v

test-quick:
	$(PYTHON) -m pytest -q --tb=short

test-watch:
	$(PYTHON) -m pytest-watch

docker-up:
	docker compose up --build

docker-down:
	docker compose down

.PHONY: install install-dev mongo-up mongo-down run up down test test-unit test-coverage test-coverage-xml test-quick test-watch docker-up docker-down
