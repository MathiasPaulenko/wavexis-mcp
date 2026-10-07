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
# cdpwave reads CDPWAVE_BROWSER_PATH to locate the browser binary.
ENV CDPWAVE_BROWSER_PATH=/usr/bin/chromium
ENV WAVEXIS_MCP_OUTPUT_DIR=/home/wavexis/output
# The CDP backend adds --no-sandbox when CI-like env vars are present, which is
# required for Chrome to launch inside a container as a non-root user.
ENV CI=true
EXPOSE 8765

USER wavexis

# Run in HTTP mode with the core capability tier by default.
# Containers need --allow-remote to be reachable through port mapping.
ENTRYPOINT ["wavexis-mcp", "--transport=http", "--allow-remote", "--port=8765", "--caps=core"]

# The SSE endpoint returns headers immediately; checking the status avoids
# blocking on the infinite event stream.
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; assert urllib.request.urlopen('http://localhost:8765/sse').status == 200" || exit 1
