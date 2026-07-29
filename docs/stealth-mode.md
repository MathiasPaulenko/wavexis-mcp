# Stealth Mode

WaveXisMCP includes a stealth mode that hides browser automation fingerprints, making it harder for anti-bot systems to detect that the browser is being controlled programmatically.

## What stealth mode does

When enabled, stealth mode:

- Removes `navigator.webdriver` property
- Falsifies `navigator.plugins` (mimics real Chrome plugins)
- Falsifies `navigator.languages` (uses realistic language list)
- Patches `window.chrome` runtime object
- Overrides `Permissions.query` to return expected results
- Masks `WebGL vendor` and `renderer` strings

## Enabling stealth mode

Pass `stealth=true` when opening a session:

=== "MCP tool call"

    ```json
    {
      "tool": "wavexis_session_open",
      "input": {
        "stealth": true,
        "headless": false
      }
    }
    ```

=== "Python"

    ```python
    from wavexis_mcp.server import create_server

    mcp = create_server(caps="all")
    # The LLM calls wavexis_session_open with stealth=true
    ```

## When to use stealth mode

| Scenario | Use stealth? | Why |
| --- | --- | --- |
| Scraping public data | Yes | Avoid bot detection |
| Testing your own site | No | Not needed |
| Form filling automation | Yes | Avoid CAPTCHAs |
| Screenshot generation | No | Not needed |
| Accessing geo-restricted content | Yes | Avoid fingerprinting |

## Limitations

Stealth mode is **not** a complete anti-detection solution:

- It does **not** bypass CAPTCHAs (reCAPTCHA, hCaptcha, Cloudflare Turnstile)
- It does **not** bypass Cloudflare's Bot Fight Mode
- It does **not** mask your IP address — use a proxy for that

### Using a proxy with stealth

Combine stealth with a proxy for better anonymity:

```json
{
  "tool": "wavexis_session_open",
  "input": {
    "stealth": true,
    "proxy": "http://user:pass@proxy-host:8080"
  }
}
```

## Headless vs headed

Stealth mode works best with a **headed** browser (`headless=false`). Some anti-bot systems detect headless Chrome even with stealth patches applied.

```json
{
  "tool": "wavexis_session_open",
  "input": {
    "stealth": true,
    "headless": false
  }
}
```

## connect_existing + stealth

For maximum stealth, connect to an existing browser that was launched manually with debug port enabled:

```bash
# Launch Chrome with debug port
chrome --remote-debugging-port=9222
```

```json
{
  "tool": "wavexis_session_open",
  "input": {
    "connect_existing": true,
    "browser_url": "http://localhost:9222",
    "stealth": true
  }
}
```

This uses a real browser profile with real history, cookies, and extensions — the hardest to detect.
