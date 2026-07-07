# Docker Deployment

WaveXisMCP provides a Docker image for HTTP transport deployment. The image includes Chromium, so no browser installation is needed on the host.

## Quick Start

```bash
# Pull and run
docker run -p 8765:8765 ghcr.io/mathiaspaulenko/wavexis-mcp

# Or build locally
docker build -t wavexis-mcp .
docker run -p 8765:8765 wavexis-mcp
```

## Docker Compose

```yaml
services:
  wavexis-mcp:
    build: .
    ports:
      - "8765:8765"
    environment:
      - WAVEXIS_BROWSER_PATH=/usr/bin/chromium
```

```bash
docker-compose up
```

## Image Details

- **Base**: `python:3.12-slim`
- **Browser**: Chromium (via apt)
- **Port**: 8765
- **Entry point**: `wavexis-mcp --transport=http --host=0.0.0.0 --port=8765 --caps=all`

## Building from Source

```bash
# Build the wheel first
python -m build --wheel

# Build the Docker image
docker build -t wavexis-mcp .
```

The Dockerfile copies the wheel from `dist/` and installs it. Make sure to run `python -m build` before `docker build`.

## CI/CD

The GitHub Actions workflow (`.github/workflows/docker.yml`) automatically builds and pushes the Docker image to GHCR when a `v*` tag is pushed:

```bash
git tag v0.2.0
git push origin v0.2.0
```

This creates:
- `ghcr.io/mathiaspaulenko/wavexis-mcp:latest`
- `ghcr.io/mathiaspaulenko/wavexis-mcp:v0.2.0`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WAVEXIS_BROWSER_PATH` | `/usr/bin/chromium` | Path to Chromium binary |
