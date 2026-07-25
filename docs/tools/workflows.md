# Workflows Tools (6)

Enable with `--caps=workflows`.

These 6 tools are added when the `workflows` capability tier is enabled.

## Workflows

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_browser_context_close` | `session_id, context_id` | Close an isolated browser context. |
| `wavexis_browser_context_create` | `session_id` | Create an isolated browser context within a session. |
| `wavexis_browser_context_list` | `session_id` | List all browser contexts in a session. |
| `wavexis_multi_action` | `config, session_id?, backend?, headless?, continue_on_error?` | Execute multiple actions from a YAML config sequentially. |
| `wavexis_raw_bidi` | `session_id, method, params?` | Send a raw BiDi command (escape hatch). |
| `wavexis_raw_cdp` | `session_id, method, params?` | Send a raw CDP command (escape hatch). |
