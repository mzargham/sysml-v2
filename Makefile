.PHONY: help install dev test lint build clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install in editable mode
	uv pip install -e .

dev: ## Install in editable mode with dev dependencies
	uv pip install -e ".[dev]"

test: ## Run tests
	uv run pytest -v

lint: ## Lint with ruff
	uv run ruff check src/ tests/

build: ## Build the package
	uv build

clean: ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info src/*.egg-info .venv __pycache__
