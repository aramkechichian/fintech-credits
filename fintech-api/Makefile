install:
	python3 -m pip install --upgrade pip setuptools wheel
	python3 -m pip install -e .

install-dev:
	python3 -m pip install --upgrade pip setuptools wheel
	python3 -m pip install -e ".[dev]"

mongo-up:
	@echo "Starting MongoDB..."
	@docker compose up -d mongodb || echo "MongoDB already running or Docker not available"

mongo-down:
	@echo "Stopping MongoDB..."
	@docker compose stop mongodb || true

run: install mongo-up
	python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

up: install mongo-up
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info

down: mongo-down
	pkill -f "python3 -m uvicorn app.main:app" || true

# Testing commands
test:
	python3 -m pytest -v

test-unit:
	python3 -m pytest tests/unit -v

test-coverage:
	python3 -m pytest --cov=app --cov-report=html --cov-report=term-missing -v

test-coverage-xml:
	python3 -m pytest --cov=app --cov-report=xml --cov-report=term-missing -v

test-quick:
	python3 -m pytest -q --tb=short

test-watch:
	python3 -m pytest-watch

docker-up:
	docker compose up --build

docker-down:
	docker compose down

.PHONY: install install-dev mongo-up mongo-down run up down test test-unit test-coverage test-coverage-xml test-quick test-watch docker-up docker-down
