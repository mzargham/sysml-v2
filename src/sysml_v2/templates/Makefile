.PHONY: help install serve-up serve-down serve-logs validate lab test lint clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	uv sync

serve-up: ## Start the SysML v2 API server
	sysml serve up

serve-down: ## Stop the SysML v2 API server
	sysml serve down

serve-logs: ## Tail API server logs
	sysml serve logs

validate: ## Validate all SysML models
	sysml validate models/

lab: ## Launch JupyterLab
	uv run jupyter lab --notebook-dir=notebooks

test: ## Run Python tests
	uv run pytest scripts/ -v

lint: ## Lint Python files with ruff
	uv run ruff check scripts/ notebooks/

clean: ## Remove generated artifacts
	rm -rf .venv __pycache__ .eggs *.egg-info dist build
