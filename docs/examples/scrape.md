# Scrape Examples

Scraping extracts text or HTML content from web pages. WaveXisMCP provides both stateless one-shot scraping and session-based crawling with depth control.

## Single URL (stateless)

The simplest case — scrape one URL without managing a session:

```text
wavexis_scrape(
    url="https://example.com",
    selector="article",
    output_format="text"
)
```

Returns the text content of the `<article>` element. The browser launches, navigates, scrapes, and closes automatically.

**When to use**: Quick content extraction from a single page where you know the CSS selector.

## Multiple URLs (batch)

Scrape multiple URLs in a single call. The browser processes each URL sequentially:

```text
wavexis_scrape(
    urls=["https://example.com", "https://example.org"],
    selector="main",
    output_format="html"
)
```

Returns HTML content for each URL. Useful for batch content extraction.

**When to use**: When you need the same selector applied to multiple pages (e.g., scraping product pages from a list).

## Crawl with depth

For deeper crawling that follows links, use `wavexis_crawl`. This requires a session and the `data` capability tier:

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_crawl(
    session_id="abc-123",
    start_url="https://docs.example.com",
    max_depth=2,
    max_pages=10,
    selector="main",
    same_origin=true
)
→ {"pages": [
    {"url": "https://docs.example.com", "content": "..."},
    {"url": "https://docs.example.com/guide", "content": "..."},
    {"url": "https://docs.example.com/api", "content": "..."},
    ...
]}

wavexis_session_close(session_id="abc-123")
```

Requires `--caps=data`.

**Parameters explained**:

- `max_depth=2` — Follow links up to 2 levels deep from the start URL
- `max_pages=10` — Stop after scraping 10 pages
- `selector="main"` — Extract only the `<main>` element from each page (reduces noise)
- `same_origin=true` — Only follow links on the same domain (prevents crawling external sites)

**When to use**: Documentation scraping, sitemap generation, content migration, building a knowledge base from a website.

## Scrape with JavaScript rendering

Some pages require JavaScript to render content. Use a session and wait for the content to load:

```text
wavexis_session_open(backend="cdp")
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://spa.example.com", wait_until="networkidle")
wavexis_wait(session_id="abc-123", strategy="selector", selector="[data-loaded]")
wavexis_scrape(
    session_id="abc-123",
    selector=".dynamic-content",
    output_format="text"
)

wavexis_session_close(session_id="abc-123")
```

**When to use**: Single-page applications (SPAs), pages that load content via AJAX, or pages that require user interaction before showing content.

## Output formats

| Format | Description |
|--------|-------------|
| `text` | Plain text content (innerText). Strips HTML tags. Best for reading content. |
| `html` | Raw HTML (outerHTML). Preserves structure and attributes. Best for re-processing or migration. |
