# Data Tools (6)

Enable with `--caps=data`.

Data tools focus on extraction and analysis. Record browser actions to YAML (codegen for test generation), run Lighthouse audits, extract structured data via CSS selectors, intercept WebSocket messages, crawl multiple URLs with depth control, and compare screenshots for visual regression testing.

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_record` | `session_id`, `output_path` | Start recording browser actions to YAML. Each click, fill, navigate is captured. Call again to stop and save. Useful for codegen — generate test scripts from manual interaction. |
| `wavexis_lighthouse` | `session_id`, `url`, `categories`, `output_path` | Run a Lighthouse audit. `categories`: list of `performance`, `accessibility`, `seo`, `best-practices`. Returns scores (0-100) and detailed metrics. |
| `wavexis_extract` | `session_id`, `selector`, `attributes`, `schema` | Extract structured data from a page. `selector`: CSS selector for items. `attributes`: list of attributes to extract. `schema`: optional JSON schema for structured extraction. |
| `wavexis_websocket_intercept` | `session_id`, `url_pattern`, `direction` | Intercept WebSocket messages. `url_pattern`: glob to match WS URLs. `direction`: `send`, `receive`, or `both`. Returns messages as JSON. |
| `wavexis_crawl` | `session_id`, `start_url`, `max_depth`, `max_pages`, `selector`, `same_origin` | Crawl multiple URLs starting from `start_url`. Follows links up to `max_depth` levels. `max_pages`: limit. `selector`: extract only this element from each page. `same_origin`: only follow same-origin links. |
| `wavexis_visual_diff` | `session_id`, `baseline`, `current`, `threshold` | Compare two screenshots for visual regression. `baseline`/`current`: file paths or base64. `threshold`: pixel difference tolerance (0-1). Returns diff image and pass/fail. |

!!! example "Run a Lighthouse audit"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_lighthouse(
        session_id="abc-123",
        url="https://example.com",
        categories=["performance", "accessibility", "seo"]
    )
    → {"scores": {"performance": 95, "accessibility": 100, "seo": 92},
       "metrics": {"lcp": 1200, "cls": 0.05, "tbt": 50}}
    wavexis_session_close(session_id="abc-123")
    ```

!!! example "Extract product data"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_navigate(session_id="abc-123", url="https://shop.example.com")
    wavexis_extract(
        session_id="abc-123",
        selector=".product-card",
        attributes=["name", "price", "image"]
    )
    → {"items": [{"name": "Widget", "price": "$9.99", "image": "..."}, ...]}
    wavexis_session_close(session_id="abc-123")
    ```

!!! example "Crawl a documentation site"
    ```text
    wavexis_session_open(backend="cdp")
    wavexis_crawl(
        session_id="abc-123",
        start_url="https://docs.example.com",
        max_depth=2,
        max_pages=20,
        selector="main",
        same_origin=true
    )
    → {"pages": [{"url": "...", "content": "..."}, ...]}
    wavexis_session_close(session_id="abc-123")
    ```
