# Rate Limiting

WaveXisMCP implements per-session rate limiting to protect the browser from excessive tool calls (M4).

## Configuration

Rate limiting is configured via CLI flags:

```bash
# Default: 60 calls/sec, burst of 10
wavexis-mcp

# Custom: 10 calls/sec, burst of 5
wavexis-mcp --rate-limit 10 --rate-burst 5

# Disable (not recommended)
wavexis-mcp --rate-limit 999999 --rate-burst 999999
```

| Flag | Default | Description |
|------|---------|-------------|
| `--rate-limit` | `60` | Maximum tool calls per second per session |
| `--rate-burst` | `10` | Maximum burst size (tokens that can accumulate) |

## How It Works

WaveXisMCP uses a **token bucket** algorithm per session:

- Each session gets its own token bucket
- Tokens are added at the configured rate (e.g. 60/sec)
- Each tool call consumes one token
- If no tokens are available, the call is rejected with a `rate_limited` error
- The bucket can accumulate up to `--rate-burst` tokens when idle

## Per-Session Isolation

Rate limiting is **per-session**, not global. This means:

- Session A making 60 calls/sec does not affect Session B
- Each session has its own independent token bucket
- Closing a session cleans up its bucket

## Rate Limited Response

When the rate limit is exceeded, the tool returns:

```json
{
  "error": "rate_limited",
  "retry_after_ms": 16
}
```

The `retry_after_ms` field indicates how long to wait before retrying.

## Use Cases

### Conservative (testing)

```bash
wavexis-mcp --rate-limit 10 --rate-burst 3
```

### Aggressive (automation)

```bash
wavexis-mcp --rate-limit 120 --rate-burst 20
```

### Docker

```bash
docker run -p 8765:8765 ghcr.io/mathiaspaulenko/wavexis-mcp
# Rate limiting uses defaults (60/sec, burst 10)
```
