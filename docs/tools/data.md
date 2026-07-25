# Data Tools (7)

Enable with `--caps=data`.

These 7 tools are added when the `data` capability tier is enabled.

## Data extraction

| Tool | Parameters | Description |
| --- | --- | --- |
| `wavexis_core_web_vitals` | `url, session_id?, observe_ms?, budgets?, headless?, backend?` | Measure Core Web Vitals (LCP, CLS, INP) with ratings and score. |
| `wavexis_crawl` | `start_url, max_depth?, max_pages?, same_origin?, url_pattern?, session_id?, wait_timeout?, headless?, backend?` | Crawl a website starting from a URL. |
| `wavexis_extract` | `url, schema, selector?, session_id?, wait_timeout?, headless?, backend?` | Extract structured data from a page using a CSS selector schema. |
| `wavexis_lighthouse` | `url, categories?, session_id?, wait_timeout?, headless?, backend?` | Run a Lighthouse-style audit on a URL. |
| `wavexis_record` | `url, duration?, headless?, backend?` | Record browser interactions and generate a YAML workflow. |
| `wavexis_visual_diff` | `url, baseline_path, selector?, threshold?, output_path?, session_id?, wait_timeout?, headless?, backend?` | Compare a screenshot against a baseline image. |
| `wavexis_websocket_intercept` | `url, url_pattern?, duration_ms?, mock_responses?, session_id?, wait_timeout?, headless?, backend?` | Capture WebSocket frames on a page. |
