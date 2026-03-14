#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-.}"
IMAGE="insightforge:local"

# Kiểm tra image đã được build chưa
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "[InsightForge] Image chưa được build. Chạy trước:"
  echo "  docker build -t $IMAGE ."
  exit 1
fi

# Auto-detect GPU
GPU_FLAG=""
echo -n "[InsightForge] Detecting GPU... "
if docker run --rm --gpus all --entrypoint true "$IMAGE" 2>/dev/null; then
  GPU_FLAG="--gpus all"
  echo "GPU ✓ (CUDA mode)"
else
  echo "not found → CPU mode"
fi

# Chạy insightforge
docker run --rm -it $GPU_FLAG \
  -v "$(cd "$PROJECT_DIR" && pwd -P):/workspace" \
  -v insightforge_data:/root/.insightforge \
  -e GITHUB_TOKEN="${GITHUB_TOKEN:-}" \
  "$IMAGE" /workspace
