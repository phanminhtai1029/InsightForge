.PHONY: setup run test docker-build docker-run docker-run-gpu clean help

# Folder mặc định để analyze
PROJECT_DIR ?= .

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

setup: ## One-line native install (macOS/Linux/WSL2)
	bash install.sh

run: ## Run InsightForge on current directory (native)
	insightforge .

test: ## Run test suite
	uv run pytest tests/ -v

docker-build: ## Build Docker image
	docker build -t insightforge:local .

docker-run: ## Run via Docker, host Ollama (CPU or GPU on host)
	@echo "Analyzing: $(PROJECT_DIR)"
	PROJECT_DIR="$(PROJECT_DIR)" docker compose run --rm insightforge /workspace

docker-run-gpu: ## Run via Docker + Ollama in container with NVIDIA GPU
	@echo "GPU mode — requires NVIDIA Container Toolkit"
	PROJECT_DIR="$(PROJECT_DIR)" docker compose \
	  -f docker-compose.yml -f docker-compose.gpu.yml \
	  run --rm insightforge /workspace

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
