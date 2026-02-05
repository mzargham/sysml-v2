.PHONY: help setup install install-all server-up server-down server-pull server-logs lab test lint clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

setup: ## Run the full bootstrap (install deps, clone repos, pull Docker images)
	@chmod +x setup.sh && ./setup.sh

install: ## Install Python dependencies (core only)
	uv sync

install-all: ## Install all Python dependencies including optional extras
	uv sync --all-extras

# ---------------------------------------------------------------------------
# Docker — Local API Server
# ---------------------------------------------------------------------------

server-up: ## Start the SysML v2 API server (PostgreSQL + API on port 9000)
	docker compose -f docker/docker-compose.yml up -d

server-down: ## Stop the SysML v2 API server
	docker compose -f docker/docker-compose.yml down

server-pull: ## Pull latest Docker images
	docker compose -f docker/docker-compose.yml pull

server-logs: ## Tail API server logs
	docker compose -f docker/docker-compose.yml logs -f api-server

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------

lab: ## Launch JupyterLab
	uv run jupyter lab --notebook-dir=notebooks

test: ## Run Python tests
	uv run pytest scripts/ -v

lint: ## Lint Python files with ruff
	uv run ruff check scripts/ notebooks/

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean: ## Remove generated artifacts (venv, caches, docker volumes)
	rm -rf .venv __pycache__ .eggs *.egg-info dist build
	docker compose -f docker/docker-compose.yml down -v 2>/dev/null || true
