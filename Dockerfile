FROM ollama/ollama:latest

# Cài uv (quản lý Python + deps)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Layer 1: cài Python deps — chỉ rebuild khi pyproject.toml / uv.lock thay đổi
COPY pyproject.toml uv.lock README.md .python-version ./
RUN uv sync --no-dev --frozen --no-install-project

# Layer 2: bake models vào image — ĐẶT TRƯỚC source code để cache models
# không bị invalidate khi sửa source code
ARG LLM=qwen2.5:7b
ARG EMBED=nomic-embed-text

RUN ollama serve & OLLAMA_PID=$! && \
    for i in $(seq 1 30); do \
      ollama list >/dev/null 2>&1 && break; \
      sleep 1; \
    done && \
    ollama pull ${LLM} && \
    ollama pull ${EMBED}; \
    MODEL_EXIT=$?; \
    kill $OLLAMA_PID 2>/dev/null; \
    wait $OLLAMA_PID 2>/dev/null; \
    exit $MODEL_EXIT

# Bake model names as runtime ENV so Config picks them up automatically
ENV INSIGHTFORGE_LLM=${LLM}
ENV INSIGHTFORGE_EMBED=${EMBED}

# Layer 3: source code — thay đổi thường xuyên nhưng không ảnh hưởng model cache
COPY insightforge/ ./insightforge/
RUN uv sync --no-dev --frozen --no-editable

# entrypoint sẽ start ollama + exec insightforge
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH"

VOLUME ["/workspace"]
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/workspace"]
