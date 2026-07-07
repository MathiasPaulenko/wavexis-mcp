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

The server starts on port 8765 with all capability tiers enabled. Connect from any MCP client via HTTP+SSE transport.

## Docker Compose

For persistent deployments with environment configuration:

```yaml
services:
  wavexis-mcp:
    build: .
    ports:
      - "8765:8765"
    environment:
      - WAVEXIS_BROWSER_PATH=/usr/bin/chromium
    restart: unless-stopped
```

```bash
docker-compose up
```

## Image Details

- **Base**: `python:3.12-slim`
- **Browser**: Chromium (via apt, ~100MB)
- **Port**: 8765
- **Entry point**: `wavexis-mcp --transport=http --host=0.0.0.0 --port=8765 --caps=all`
- **Image size**: ~350MB (Python + Chromium + wavexis-mcp)

The image bundles Chromium so it works out of the box in any environment — no browser installation needed on the host.

## Building from Source

```bash
# Build the wheel first
python -m build --wheel

# Build the Docker image
docker build -t wavexis-mcp .
```

The Dockerfile copies the wheel from `dist/` and installs it. Make sure to run `python -m build` before `docker build`.

## CI/CD

The GitHub Actions release workflow (`.github/workflows/release.yml`) automatically builds and pushes the Docker image to GHCR when a version tag (`v*.*.*`) is pushed:

```bash
git tag v1.4.0
git push origin v1.4.0
```

This creates:

- `ghcr.io/mathiaspaulenko/wavexis-mcp:latest`
- `ghcr.io/mathiaspaulenko/wavexis-mcp:v1.4.0`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WAVEXIS_BROWSER_PATH` | `/usr/bin/chromium` | Path to Chromium binary inside the container |
| `WAVEXIS_BACKEND` | `cdp` | Default backend: `cdp` or `bidi` |

## Use cases

- **CI/CD pipelines** — Run browser automation tests in isolation
- **Shared instance** — Deploy on a server for multiple LLM clients to connect
- **Development** — Consistent environment across team members
- **Testing** — Reproducible browser environment for regression testing
