.PHONY: help up down test test-coverage test-unit bash
APP_NAME ?= fintech-api
COMPOSE_FILE := docker-compose.yml

# ====================================================================================================
# Local Development - Day-to-Day Commands (macOS + Linux)
# ====================================================================================================

help:
	@echo "Commands:"
	@echo "  up            : Starts API + MongoDB (docker compose up --build)."
	@echo "  down          : Stops and removes containers and volumes."
	@echo "  test          : Runs tests inside the API container."
	@echo "  test-coverage : Runs tests with coverage report."
	@echo "  test-unit     : Runs unit tests only."
	@echo "  bash          : Opens a shell in the API container."

up:
	@echo "Starting $(APP_NAME) and MongoDB..."
	@docker compose -f $(COMPOSE_FILE) up --build

down:
	@echo "Stopping $(APP_NAME) services..."
	@docker compose -f $(COMPOSE_FILE) down -v

test:
	@echo "Running tests..."
	@docker compose -f $(COMPOSE_FILE) run -T --rm api python -m pytest -v

test-coverage:
	@echo "Running tests with coverage..."
	@docker compose -f $(COMPOSE_FILE) run -T --rm api python -m pytest --cov=app --cov-report=term-missing --cov-report=html -v

test-unit:
	@echo "Running unit tests..."
	@docker compose -f $(COMPOSE_FILE) run -T --rm api python -m pytest tests/unit -v

bash:
	@echo "Opening container shell..."
	@docker compose -f $(COMPOSE_FILE) exec api bash
