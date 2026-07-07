# MCP Resources & Prompts

WaveXisMCP exposes browser state as MCP resources and workflow templates as MCP prompts (M3).

## Resources

Resources are read-only data exposed to LLMs via the `wavexis://` URI scheme.

### Available Resources

| URI | Description |
|-----|-------------|
| `wavexis://session/{session_id}/url` | Current page URL |
| `wavexis://session/{session_id}/cookies` | Cookies as JSON |
| `wavexis://session/{session_id}/console` | Console messages as JSON |
| `wavexis://session/{session_id}/tabs` | Open tabs as JSON |

### Usage

Resources are automatically available when a session is open. MCP clients can read them at any time:

```
GET wavexis://session/abc-123/url
→ "https://example.com"

GET wavexis://session/abc-123/cookies
→ [{"name": "session", "value": "abc"}]
```

### Read-Only

Resources are strictly read-only. They cannot mutate browser state. Use tools for any state-changing operations.

## Prompts

Prompts are workflow templates that guide LLMs through common multi-step tasks.

### Available Prompts

#### `scrape_page(url, selector="body")`

Scrapes a page and extracts content. Guides the LLM through:

1. Open a session
2. Navigate to the URL
3. Scrape with the selector
4. Close the session
5. Return extracted content

#### `audit_page(url)`

Runs a full accessibility and performance audit. Guides the LLM through:

1. Open a session with a11y + devtools tiers
2. Navigate to the URL
3. Run axe-core audit
4. Get performance metrics
5. Take a11y snapshot
6. Summarize findings

#### `fill_form(url, fields)`

Fills a form on a page. Guides the LLM through:

1. Open a session
2. Navigate to the URL
3. Take a11y snapshot to identify fields
4. Fill each field
5. Screenshot to verify
6. Report results

#### `debug_page(url)`

Debugs a page (console, network, performance). Guides the LLM through:

1. Open a session with network + devtools tiers
2. Navigate to the URL
3. Capture console messages
4. List network requests
5. Get performance metrics
6. Check security state
7. Summarize issues

### Templates Only

Prompts are templates — they do not execute actions themselves. The LLM receives the template and uses the listed tools to perform the workflow.
