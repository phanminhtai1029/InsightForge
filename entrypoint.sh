#!/usr/bin/env bash
# Gợi ý GPU nếu có NVIDIA nhưng không set OLLAMA_HOST
if [ -z "${OLLAMA_HOST:-}" ]; then
  if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null 2>&1; then
    echo "[InsightForge] NVIDIA GPU detected. Consider GPU mode:"
    echo "  docker compose -f docker-compose.yml -f docker-compose.gpu.yml run insightforge"
  fi
fi
exec "$@"
