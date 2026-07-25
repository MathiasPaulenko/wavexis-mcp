FROM python:3.12-slim AS builder

WORKDIR /build
COPY . .
RUN pip install --no-cache-dir build && python -m build --wheel

FROM python:3.12-slim

# Install Chromium
RUN apt-get update && \
    apt-get install -y --no-install-recommends chromium && \
    rm -rf /var/lib/apt/lists/*

# Install wavexis-mcp (wheel filename uses PEP 625 normalized package name)
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl

# Create a non-root user and a writable output directory
RUN useradd -m -u 1000 wavexis && \
    mkdir -p /home/wavexis/output && \
    chown -R wavexis:wavexis /home/wavexis
WORKDIR /home/wavexis
ENV WAVEXIS_BROWSER_PATH=/usr/bin/chromium
ENV WAVEXIS_MCP_OUTPUT_DIR=/home/wavexis/output
# The CDP backend adds --no-sandbox when CI-like env vars are present, which is
# required for Chrome to launch inside a container as a non-root user.
ENV CI=true
EXPOSE 8765

USER wavexis

# Run in HTTP mode with the core capability tier by default.
# Use --caps=all or --allow-remote only after reviewing the security implications.
ENTRYPOINT ["wavexis-mcp", "--transport=http", "--host=0.0.0.0", "--port=8765", "--caps=core"]

# Basic health check using Python's stdlib (no extra curl dependency).
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8765/').read()" || exit 1
