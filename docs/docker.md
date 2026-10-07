# Docker Deployment

WaveXisMCP provides a Docker image for HTTP transport deployment. The image includes Chromium, so no browser installation is needed on the host. This is the easiest way to deploy WaveXisMCP as a shared instance or in CI/CD pipelines.

## Quick Start

```bash
# Pull and run
docker run -p 8765:8765 ghcr.io/mathiaspaulenko/wavexis-mcp

# Or build locally
docker build -t wavexis-mcp .
docker run -p 8765:8765 wavexis-mcp
```

The server starts on port 8765 with core capability tiers enabled. Use `--caps=all` when running the image to enable every tier.

## Docker Compose

For persistent deployments with environment configuration:

```yaml
services:
  wavexis-mcp:
    build: .
    ports:
      - "127.0.0.1:8765:8765"
    environment:
      - CDPWAVE_BROWSER_PATH=/usr/bin/chromium
      - WAVEXIS_MCP_OUTPUT_DIR=/home/wavexis/output
      - CI=true
    volumes:
      - ./output:/home/wavexis/output
    restart: unless-stopped
```

```bash
docker-compose up
```

## Image Details

- **Base**: `python:3.12-slim`
- **Browser**: Chromium (via apt, ~100MB)
- **Port**: 8765
- **Entry point**: `wavexis-mcp --transport=http --allow-remote --port=8765 --caps=core` (use `--caps=all` only after reviewing security implications)
- **Image size**: ~350MB (Python + Chromium + wavexis-mcp)

The image bundles Chromium so it works out of the box in any environment — no browser installation needed on the host.

## Building from Source

```bash
# The Dockerfile is multi-stage: it builds the wheel inside the image.
docker build -t wavexis-mcp .
```

## CI/CD

The GitHub Actions release workflow (`.github/workflows/release.yml`) automatically builds and pushes the Docker image to GHCR when a version tag (`v*.*.*`) is pushed:

```bash
git tag v1.6.8
git push origin v1.6.8
```

This creates:

- `ghcr.io/mathiaspaulenko/wavexis-mcp:latest`
- `ghcr.io/mathiaspaulenko/wavexis-mcp:v1.6.8`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CDPWAVE_BROWSER_PATH` | `/usr/bin/chromium` | Path to Chromium binary inside the container |
| `WAVEXIS_MCP_OUTPUT_DIR` | `/home/wavexis/output` | Base directory for file outputs |
| `CI` | `true` | Enables Chrome `--no-sandbox` flag for container compatibility |

## Use cases

- **CI/CD pipelines** — Run browser automation tests in isolation
- **Shared instance** — Deploy on a server for multiple LLM clients to connect
- **Development** — Consistent environment across team members
- **Testing** — Reproducible browser environment for regression testing
