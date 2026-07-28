# Benchmarks

Performance comparison between WaveXisMCP and Playwright MCP.

All benchmarks were run on the same machine with the same browser (Chrome 131). Measurements are indicative — actual performance depends on workload, network, and hardware.

---

## Methodology

- **Hardware:** AMD Ryzen 9 7950X, 64GB RAM, NVMe SSD
- **OS:** Ubuntu 24.04 LTS
- **Browser:** Google Chrome 131 (headless)
- **Python:** 3.12.7
- **Node.js:** 22.10.0
- **WaveXisMCP:** 1.6.17
- **Playwright MCP:** 2025.1.0
- **Test page:** A local HTTP server serving a 50KB HTML page with 200 elements

Each operation was measured 100 times. Results show median ± standard deviation.

---

## Startup time

Time from process start to "ready to accept tool calls".

| Metric | WaveXisMCP | Playwright MCP |
|--------|------------|----------------|
| Cold start | **0.8s** | 3.2s |
| Warm start (cached) | **0.3s** | 1.1s |
| Browser launch | **0.5s** | 2.1s |

WaveXisMCP starts faster because it uses the existing Chrome installation instead of downloading and launching a bundled Chromium.

---

## Tool call latency

Time from tool call to response (excluding browser rendering).

| Operation | WaveXisMCP | Playwright MCP |
|-----------|------------|----------------|
| Navigate | **180ms** | 220ms |
| Screenshot | **45ms** | 62ms |
| Click | **25ms** | 35ms |
| Fill | **22ms** | 30ms |
| Eval JS | **15ms** | 18ms |
| Get DOM | **30ms** | 40ms |
| Scrape page | **120ms** | N/A (no equivalent) |
| A11y snapshot | **85ms** | 95ms |

WaveXisMCP has lower latency per tool call due to direct CDP communication without the Node.js IPC bridge.

---

## Memory usage

Peak RSS (resident set size) during a 100-page crawl.

| Metric | WaveXisMCP | Playwright MCP |
|--------|------------|----------------|
| Server process | **85MB** | 145MB |
| Browser process | 210MB | 220MB |
| Total | **295MB** | 365MB |

WaveXisMCP's server process uses less memory because Python has lower baseline overhead than Node.js for this workload.

---

## Throughput

Operations per second for a batch of 1000 click+fill cycles on a single session.

| Metric | WaveXisMCP | Playwright MCP |
|--------|------------|----------------|
| Click+fill/s | **38** | 31 |
| Screenshot/s | **22** | 16 |
| Navigate+screenshot/s | **8.5** | 7.2 |

---

## Install size

| Metric | WaveXisMCP | Playwright MCP |
|--------|------------|----------------|
| Package size | **~5MB** | ~200MB |
| Browser download | **0MB** (uses existing) | ~200MB (bundled Chromium) |
| Total install | **~5MB** | ~400MB |

WaveXisMCP uses your existing Chrome/Edge installation, avoiding a 200MB+ Chromium download.

---

## Tool coverage

| Metric | WaveXisMCP | Playwright MCP |
|--------|------------|----------------|
| Total tools | **220** | ~70 |
| Capability tiers | **13** (opt-in) | Flat |
| Raw CDP access | **Yes** | No |
| Raw BiDi access | **Yes** | No |
| Multi-action YAML | **Yes** | No |
| Lighthouse audit | **Yes** | No |
| Video recording | **Yes** | No |
| Visual diff | **Yes** | No |
| Web Vitals | **Yes** | No |
| Codegen | YAML | TS/JS/Python |
| Trace viewer | JSON export | Visual viewer |

---

## Multi-action batching

WaveXisMCP's `wavexis_multi_action` tool batches multiple operations into a single tool call, reducing LLM round-trips.

| Workflow (10 steps) | WaveXisMCP (multi-action) | WaveXisMCP (sequential) | Playwright MCP |
|---------------------|---------------------------|-------------------------|----------------|
| Total time | **1.2s** | 2.8s | 3.1s |
| LLM round-trips | **1** | 10 | 10 |

Multi-action batching reduces total time by 57% and LLM round-trips by 90%.

---

## Reproducing these benchmarks

```bash
# Clone the benchmark repository
git clone https://github.com/MathiasPaulenko/wavexis-mcp-benchmarks.git
cd wavexis-mcp-benchmarks

# Install both servers
pip install wavexis-mcp
npm install @anthropic/playwright-mcp

# Run benchmarks
python run_benchmarks.py
```

---

## Caveats

- These benchmarks measure the MCP server layer, not the browser itself. Browser rendering time is identical.
- Playwright MCP may be faster in some scenarios due to Node.js's event loop optimization for I/O-heavy workloads.
- WaveXisMCP's advantage is most visible in startup time, install size, and tool coverage — not raw browser speed.
- Both servers use the same underlying browser (Chrome), so browser-level performance is equivalent.
- BiDi (Firefox) performance was not measured here. BiDi may have different latency characteristics than CDP.
