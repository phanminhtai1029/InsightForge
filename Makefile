.PHONY: setup run run-win test docker-build docker-build-custom clean help

# Folder mặc định để analyze
PROJECT_DIR ?= .
LLM         ?= qwen2.5:7b
EMBED       ?= nomic-embed-text

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

setup: ## One-line native install (macOS/Linux/WSL2)
	bash install.sh

run: ## Auto-detect GPU và chạy (Linux/Mac/WSL2)
	bash run.sh $(PROJECT_DIR)

run-win: ## Auto-detect GPU và chạy (Windows PowerShell)
	powershell -File run.ps1 $(PROJECT_DIR)

test: ## Run test suite
	uv run pytest tests/ -v

docker-build: ## Build Docker image (default: qwen2.5:7b + nomic-embed-text)
	docker build -t insightforge:local .

docker-build-custom: ## Build với model tùy chọn (make docker-build-custom LLM=llama3.2)
	docker build \
	  --build-arg LLM=$(LLM) \
	  --build-arg EMBED=$(EMBED) \
	  -t insightforge:local .

clean: ## Remove build artifacts và caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
