FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

# Install deps (no dev, no editable)
RUN uv sync --no-dev --frozen

# Copy source code
COPY insightforge/ ./insightforge/

# GPU detection + exec wrapper
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Activate venv on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Default: analyze /workspace (mounted by user)
VOLUME ["/workspace"]
ENTRYPOINT ["/entrypoint.sh", "insightforge"]
CMD ["/workspace"]
