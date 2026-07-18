# Developer shortcuts — run `make help` for the list.
.DEFAULT_GOAL := help

.PHONY: help up down logs ps clean lint test

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

lint: ## Lint the Python services
	cd backend && ruff check .

test: ## Run the backend test suite
	cd backend && pytest
