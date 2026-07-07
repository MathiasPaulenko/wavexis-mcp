# Workflows Tools (5)

Enable with `--caps=workflows`.

Workflow tools provide advanced automation capabilities: execute multi-action YAML sequences in a single tool call, send raw CDP or BiDi commands as an escape hatch for any browser feature, and manage isolated browser contexts for parallel sessions.

## Multi-action

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_multi_action` | `session_id`, `actions`, `continue_on_error` | Execute a sequence of actions in one call. `actions`: list of action dicts. `continue_on_error`: if `true`, keeps executing after failures. |

Supported action types: `navigate`, `screenshot`, `eval`, `click`, `type`, `fill`, `wait`.

## Raw protocol access

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_raw_cdp` | `session_id`, `method`, `params` | Send a raw CDP (Chrome DevTools Protocol) command. `method`: CDP method name (e.g., `Page.reload`). `params`: dict of parameters. Escape hatch for any CDP feature not covered by a dedicated tool. |
| `wavexis_raw_bidi` | `session_id`, `method`, `params` | Send a raw WebDriver BiDi command. `method`: BiDi command name. `params`: dict of parameters. Escape hatch for any BiDi feature. |

## Browser contexts

Browser contexts are isolated environments within the same browser instance. Each context has its own cookies, storage, and cache — like incognito windows. Useful for parallel sessions that shouldn't interfere with each other.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_browser_context_create` | `session_id` | Create an isolated browser context. Returns `context_id`. |
| `wavexis_browser_context_close` | `session_id`, `context_id` | Close a browser context and free its resources. |

!!! example "Multi-action workflow"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_multi_action(
        session_id="abc-123",
        actions=[
            {"type": "navigate", "url": "https://example.com"},
            {"type": "wait", "strategy": "selector", "selector": "#content"},
            {"type": "click", "selector": "#login"},
            {"type": "fill", "selector": "#email", "value": "user@example.com"},
            {"type": "screenshot"}
        ]
    )
    wavexis_session_close(session_id="abc-123")
    ```

!!! example "Raw CDP escape hatch"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_raw_cdp(
        session_id="abc-123",
        method="Emulation.setDeviceMetricsOverride",
        params={"width": 375, "height": 812, "deviceScaleFactor": 3, "mobile": true}
    )
    wavexis_session_close(session_id="abc-123")
    ```

!!! note "When to use raw protocol"
    Use `wavexis_raw_cdp` or `wavexis_raw_bidi` when you need a browser feature that doesn't have a dedicated tool. For example, CDP domains like `WebGPU`, `WebSerial`, `WebUSB` are not wrapped but can be accessed via raw commands. This is the escape hatch that ensures WaveXisMCP is never limited by its tool set.
