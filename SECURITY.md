# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in WaveXisMCP, please report it responsibly.

**Do NOT open a public GitHub issue.**

Instead, email **mathias.paulenko@outlook.com** with:

1. A description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

You will receive a response within 48 hours. If the vulnerability is confirmed, a fix will be prioritized and a security advisory will be published.

## Scope

WaveXisMCP exposes browser automation capabilities to LLMs. Security considerations:

- **Browser execution**: Tools can launch browsers, navigate to URLs, execute JavaScript, and interact with web pages. Only connect to trusted MCP clients.
- **File system access**: `output_path` and `output_dir` parameters write files under the directory configured by the `WAVEXIS_MCP_OUTPUT_DIR` environment variable, or the current working directory if unset. Paths that escape this directory, including via symlinks, are rejected.
- **URL validation**: URLs are validated before navigation to block non-HTTP schemes, private IP ranges, localhost, and cloud metadata endpoints. Discovered links during crawls are also validated. Hostname-based DNS rebinding is an inherent TOCTOU risk; set `WAVEXIS_MCP_ALLOW_INTERNAL_URLS=0` in untrusted environments.
- **Raw CDP/BiDi commands**: `wavexis_raw_cdp` and `wavexis_raw_bidi` are restricted to a read-only allowlist of safe methods by default. Set `WAVEXIS_MCP_ALLOW_RAW_COMMANDS=all` to allow arbitrary commands, or avoid enabling the `workflows` tier when the client is not fully trusted.
- **HTTP headers**: `wavexis_set_headers` and `wavexis_route` filter out headers that could be used to bypass security controls or perform request smuggling (`Host`, `Authorization`, `Cookie`, `Content-Length`, `Transfer-Encoding`, etc.).  All user-supplied header values, including extra headers passed to `SessionManager.open()` and `acquire_backend()`, are checked for CR/LF/null injection.
- **User-Agent**: `wavexis_set_user_agent` and browser launch options reject values containing CR/LF characters to prevent header injection.
- **Service workers**: `wavexis_service_worker_emulate` validates the `script_url` with the same URL rules as navigation.
- **User data directories**: `user_data_dir` values are resolved under `WAVEXIS_MCP_OUTPUT_DIR` and paths that escape it are rejected.
- **Session management**: Session IDs are UUIDs. Keep them private — anyone with a session ID can control that browser instance.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.6.x   | Yes       |
| < 1.6   | No        |
