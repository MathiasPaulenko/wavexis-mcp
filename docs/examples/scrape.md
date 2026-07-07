# Scrape Example

## Single URL

```python
wavexis_scrape(
    url="https://example.com",
    selector="article",
    output_format="text"
)
```

Returns the text content of the `<article>` element.

## Multiple URLs (batch)

```python
wavexis_scrape(
    urls=["https://example.com", "https://example.org"],
    selector="main",
    output_format="html"
)
```

Returns HTML content for each URL.

## Crawl with depth

```python
wavexis_session_open(backend="cdp")
# → {"session_id": "abc-123"}

wavexis_crawl(
    session_id="abc-123",
    start_url="https://example.com",
    max_depth=2,
    max_pages=10,
    selector="article"
)
wavexis_session_close(session_id="abc-123")
```

Requires `--caps=data`.
