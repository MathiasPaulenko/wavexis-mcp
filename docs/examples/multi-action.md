# Multi-Action Examples

Multi-action tools let you chain multiple browser actions in a single tool call, reducing round-trips between the LLM and WaveXisMCP. This is faster and more reliable than calling individual tools sequentially.

## YAML multi-action

Execute a sequence of actions in a single tool call. Each action is a dict with a `type` and type-specific parameters:

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_multi_action(
    session_id="abc-123",
    actions=[
        {"type": "navigate", "url": "https://example.com"},
        {"type": "wait", "strategy": "selector", "selector": "#content"},
        {"type": "click", "selector": "#login"},
        {"type": "fill", "selector": "#email", "value": "user@example.com"},
        {"type": "fill", "selector": "#password", "value": "secret123"},
        {"type": "click", "selector": "#submit"},
        {"type": "screenshot"}
    ]
)
→ {"results": [
    {"action": "navigate", "status": "ok"},
    {"action": "wait", "status": "ok"},
    {"action": "click", "status": "ok"},
    {"action": "fill", "status": "ok"},
    {"action": "fill", "status": "ok"},
    {"action": "click", "status": "ok"},
    {"action": "screenshot", "status": "ok", "data": "iVBORw0KGgo..."}
]}

wavexis_session_close(session_id="abc-123")
```

Requires `--caps=workflows`.

**Supported action types**: `navigate`, `screenshot`, `eval`, `click`, `type`, `fill`, `wait`.

**When to use**: When you have a known sequence of actions that don't require LLM decision-making between steps. Reduces latency by batching operations.

### Error handling

By default, multi-action stops on the first error. Set `continue_on_error=true` to keep executing:

```text
wavexis_multi_action(
    session_id="abc-123",
    actions=[
        {"type": "navigate", "url": "https://example.com"},
        {"type": "click", "selector": "#maybe-missing"},  # might fail
        {"type": "screenshot"}  # still runs
    ],
    continue_on_error=true
)
```

## Raw CDP command

Send a raw Chrome DevTools Protocol command as an escape hatch for any CDP feature not covered by a dedicated tool:

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_raw_cdp(
    session_id="abc-123",
    method="Emulation.setDeviceMetricsOverride",
    params={"width": 375, "height": 812, "deviceScaleFactor": 3, "mobile": true}
)
→ {"result": {}}

wavexis_navigate(session_id="abc-123", url="https://example.com")
wavexis_screenshot(session_id="abc-123")

wavexis_session_close(session_id="abc-123")
```

**When to use**: When you need a CDP feature that doesn't have a dedicated tool. Examples: `WebGPU`, `WebSerial`, `WebUSB`, `DeviceOrientation`, custom DevTools extensions.

## Raw BiDi command

Send a raw WebDriver BiDi command for cross-browser features:

```text
wavexis_session_open(backend="bidi")
→ {"session_id": "abc-123"}

wavexis_raw_bidi(
    session_id="abc-123",
    method="session.subscribe",
    params={"events": ["log.entryAdded"]}
)
→ {"result": {}}

wavexis_navigate(session_id="abc-123", url="https://example.com")
# Console events are now being captured

wavexis_session_close(session_id="abc-123")
```

**When to use**: When working with Firefox or when you need a BiDi-specific feature not covered by a dedicated tool.

## Browser contexts

Create isolated browser contexts for parallel testing. Each context has its own cookies, storage, and cache:

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

# Create two isolated contexts
wavexis_browser_context_create(session_id="abc-123")
→ {"context_id": "ctx-1"}
wavexis_browser_context_create(session_id="abc-123")
→ {"context_id": "ctx-2"}

# Context 1: Log in as user A
# Context 2: Log in as user B
# They don't share cookies — fully isolated

# Clean up
wavexis_browser_context_close(session_id="abc-123", context_id="ctx-1")
wavexis_browser_context_close(session_id="abc-123", context_id="ctx-2")
wavexis_session_close(session_id="abc-123")
```

**When to use**: Testing multi-user scenarios, parallel test isolation, or when you need separate sessions that shouldn't interfere with each other's state.
