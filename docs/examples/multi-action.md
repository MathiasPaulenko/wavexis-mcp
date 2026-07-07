# Multi-Action Example

## YAML multi-action

Execute a sequence of actions in a single tool call:

```python
wavexis_session_open(backend="cdp")
# → {"session_id": "abc-123"}

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

Requires `--caps=workflows`.

## Raw CDP command

Send a raw CDP command as an escape hatch:

```python
wavexis_session_open(backend="cdp")
# → {"session_id": "abc-123"}

wavexis_raw_cdp(
    session_id="abc-123",
    method="Page.reload",
    params={"ignoreCache": True}
)
wavexis_session_close(session_id="abc-123")
```

## Raw BiDi command

Send a raw WebDriver BiDi command:

```python
wavexis_session_open(backend="bidi")
# → {"session_id": "abc-123"}

wavexis_raw_bidi(
    session_id="abc-123",
    method="session.subscribe",
    params={"events": ["log.entryAdded"]}
)
wavexis_session_close(session_id="abc-123")
```
