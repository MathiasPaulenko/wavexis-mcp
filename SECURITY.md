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
- **File system access**: `output_path` and `output_dir` parameters write files to disk. MCP clients should sandbox file paths.
- **Session management**: Session IDs are UUIDs. Keep them private — anyone with a session ID can control that browser instance.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
| < 0.1   | No        |
