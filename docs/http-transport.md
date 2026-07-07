# HTTP Transport

WaveXisMCP supports two transports from a single codebase: **stdio** (default, for local development with LLM clients) and **HTTP** (for CI/CD, shared instances, and Docker deployment).

## When to use HTTP vs stdio

| Transport | Use case |
|-----------|----------|
| **stdio** (default) | Local development with Claude Desktop, Cursor, Windsurf, VS Code. The LLM client launches WaveXisMCP as a subprocess. |
| **HTTP** | CI/CD pipelines, shared instances on a server, Docker deployment, or when multiple clients need to connect to the same WaveXisMCP instance. |

## Quick Start

```bash
# Run in HTTP mode on localhost
wavexis-mcp --transport http --port 8765

# Run with all capability tiers
wavexis-mcp --transport http --port 8765 --caps all
```

## CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--transport` | `stdio` | Transport mode: `stdio` or `http` |
| `--host` | `127.0.0.1` | HTTP bind host |
| `--port` | `8765` | HTTP listen port |
| `--allow-remote` | `false` | Bind to `0.0.0.0` (enables remote access) |
| `--caps` | `core` | Comma-separated capability tiers |
| `--rate-limit` | `60` | Max tool calls per second per session |
| `--rate-burst` | `10` | Max burst size for rate limiting |

## Security

### Localhost by Default

HTTP transport binds to `127.0.0.1` by default. This means only processes on the same machine can connect.

### Remote Access

Use `--allow-remote` to bind to `0.0.0.0`:

```bash
wavexis-mcp --transport http --allow-remote --port 8765
```

**Warning**: This allows connections from any IP address. Use behind a reverse proxy with authentication.

### No Authentication (v0.2.0)

WaveXisMCP does not include built-in authentication for HTTP transport in v0.2.0. This is planned for v0.3.0. For remote deployments, use a reverse proxy (nginx, Caddy) with auth.

## Use Cases

### CI/CD Pipelines

```yaml
# GitHub Actions example
- name: Start WaveXisMCP
  run: wavexis-mcp --transport http --port 8765 --caps all &
- name: Run tests
  run: curl http://127.0.0.1:8765/sse
```

### Shared Instance

```bash
# On a VPS
wavexis-mcp --transport http --allow-remote --port 8765 --caps all
```

### Docker

```bash
docker run -p 8765:8765 ghcr.io/mathiaspaulenko/wavexis-mcp
```

See [Docker documentation](docker.md) for details.
