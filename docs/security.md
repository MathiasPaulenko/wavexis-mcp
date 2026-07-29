# Security

WaveXisMCP takes security seriously. This page covers the built-in protections and how to configure them.

## SSRF protection

All URL-based tools validate against SSRF (Server-Side Request Forgery) attacks:

- Private IP ranges (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) are blocked by default
- `localhost` and `0.0.0.0` are rejected
- IPv6 loopback (`::1`) and link-local (`fe80::/10`) are blocked
- Metadata endpoints (`169.254.169.254`) are blocked

### Allow private IPs

If you need to access internal services, set the environment variable:

```bash
export WAVEXIS_MCP_ALLOW_PRIVATE_IPS=1
```

!!! warning "Security risk"
    Enabling private IP access allows the LLM to reach internal services. Only do this in trusted environments.

## Path sandboxing

All file-writing tools (screenshots, PDFs, HAR files, videos) write to a sandboxed output directory:

- Default: current working directory
- Override with `WAVEXIS_MCP_OUTPUT_DIR=/path/to/output`
- Paths that escape the sandbox via `..` are rejected
- Absolute paths outside the sandbox are rejected

```bash
# Set a dedicated output directory
export WAVEXIS_MCP_OUTPUT_DIR=/tmp/wavexis-output
```

## Rate limiting

WaveXisMCP includes built-in rate limiting to prevent runaway tool calls:

- Default: 60 calls/minute
- Configurable via `WAVEXIS_MCP_RATE_LIMIT=120` (calls per minute)
- Set to `0` to disable

See [Rate Limiting](rate-limiting.md) for details.

## Raw protocol access

The `experimental` tier provides raw CDP/BiDi access via an allowlist:

- Only domains in the allowlist can be called
- Default allowlist: `Page`, `DOM`, `Runtime`, `Network`, `Target`
- Override with `WAVEXIS_MCP_CDP_ALLOWLIST=Page,DOM,Runtime`

!!! danger
    Raw protocol access bypasses all abstractions. Only enable `experimental` when you understand the risks.

## Stealth mode

Stealth mode hides browser automation fingerprints:

- Removes `navigator.webdriver`
- Falsifies plugins and languages
- Mimics real Chrome runtime properties
- Does **not** bypass CAPTCHAs or Cloudflare challenges by itself

Enable with:

```bash
uvx wavexis-mcp --caps all
```

Then use `stealth=true` in `wavexis_session_open`.

## Browser process isolation

Each session launches a separate browser process:

- No shared state between sessions
- Sessions are cleaned up on disconnect
- Browser processes are killed on session close
- No persistent cookies or history between sessions (unless `user_data_dir` is set)

## Reporting vulnerabilities

See [SECURITY.md](https://github.com/MathiasPaulenko/wavexis-mcp/blob/main/SECURITY.md) for the supported version table and vulnerability reporting process.
