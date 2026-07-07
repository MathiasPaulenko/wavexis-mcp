FROM python:3.12-slim

# Install Chromium
RUN apt-get update && \
    apt-get install -y --no-install-recommends chromium && \
    rm -rf /var/lib/apt/lists/*

# Install wavexis-mcp
COPY dist/wavexis_mcp-*.whl /tmp/
RUN pip install --no-cache-dir /tmp/wavexis_mcp-*.whl

# Configure
ENV WAVEXIS_BROWSER_PATH=/usr/bin/chromium
EXPOSE 8765

# Run in HTTP mode with all capability tiers
ENTRYPOINT ["wavexis-mcp", "--transport=http", "--host=0.0.0.0", "--port=8765", "--caps=all"]
