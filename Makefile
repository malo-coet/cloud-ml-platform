# Developer shortcuts — run `make help` for the list.
.DEFAULT_GOAL := help

VENV := backend/.venv

.PHONY: help up down logs ps clean deps lint test

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

up: ## Build and start the full local stack
	docker compose up -d --build

down: ## Stop the stack (data volumes are kept)
	docker compose down

logs: ## Tail logs from all services
	docker compose logs -f

ps: ## Show service status
	docker compose ps

clean: ## Stop the stack AND delete data volumes
	docker compose down -v

# Local virtualenv for lint/test — always used explicitly so the system
# Python (macOS ships an old 3.9) never leaks into the toolchain.
$(VENV):
	cd backend && python3 -m venv .venv && .venv/bin/pip install -q -e ".[dev]"

deps: $(VENV) ## (Re)install backend dev dependencies into the venv
	cd backend && .venv/bin/pip install -q -e ".[dev]"

lint: $(VENV) ## Lint the Python services
	cd backend && .venv/bin/ruff check .

test: $(VENV) ## Run the backend test suite
	cd backend && .venv/bin/pytest
