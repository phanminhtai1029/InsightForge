#!/bin/bash
set -e

echo "[InsightForge] Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Chờ Ollama sẵn sàng (tối đa 30 giây)
for i in $(seq 1 30); do
  if ollama list >/dev/null 2>&1; then
    echo "[InsightForge] Ollama ready."
    break
  fi
  sleep 1
done

if ! ollama list >/dev/null 2>&1; then
  echo "[InsightForge] WARNING: Ollama không start được sau 30s — tiếp tục với CPU chậm..."
fi

# Exec insightforge (thay thế shell process = signals hoạt động đúng)
exec insightforge "$@"
