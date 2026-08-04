# Visual Regression Examples

Visual regression testing compares a live page capture against a saved baseline image. Use `wavexis_screenshot` (core tier) to write baseline PNGs to disk, then `wavexis_visual_diff` (data tier) to navigate to a URL, capture the current page, and compare it to `baseline_path`. The diff tool does not accept a second image file — it always re-navigates and captures “current” itself. Enable visual diff with `--caps=data`. If the underlying wavexis W12 `visual_diff` action is missing, the tool returns `{"status": "not_implemented", "message": "Requires wavexis W12 visual_diff action"}` instead of diff metrics.

## Basic visual diff

The simplest regression check: save a baseline once, then call `wavexis_visual_diff` with the same URL and `baseline_path`. The tool launches a browser (or uses `session_id`), navigates to `url`, captures the page, and pixel-compares against the baseline file. Use `output_path` to persist a diff overlay image; omit it to receive `diff_base64` in the JSON response. Tune `threshold` (0.0–1.0, default `0.1`) to control per-pixel color sensitivity.

```text
# Step 1 — capture baseline (core tier)
wavexis_screenshot(
    url="https://example.com",
    full_page=false,
    output_path="./baselines/example-home.png"
)
→ {"status": "ok", "path": "./baselines/example-home.png", "size_bytes": 84210}

# Step 2 — compare live page against baseline (data tier)
wavexis_visual_diff(
    url="https://example.com",
    baseline_path="./baselines/example-home.png",
    threshold=0.1,
    output_path="./diffs/example-home-diff.png"
)
→ {
    "status": "ok",
    "diff_percentage": 0.03,
    "diff_pixels": 42,
    "passed": false,
    "total_pixels": 140000,
    "diff_path": "./diffs/example-home-diff.png"
}
```

Without `output_path`, a passing run looks like:

```text
→ {
    "status": "ok",
    "diff_percentage": 0.0,
    "diff_pixels": 0,
    "passed": true,
    "total_pixels": 140000,
    "diff_base64": "iVBORw0KGgo..."
}
```

Requires `--caps=data`.

`passed` is `true` only when `diff_pixels` is exactly `0` (no pixels exceeded `threshold`). `diff_percentage` is on a 0–100 scale (so `0.03` means 0.03%, not 3%). Open `diff_path` (or decode `diff_base64`) to see highlighted mismatch regions.

**When to use**: Smoke-testing a single page after a deploy, or verifying a UI change did not alter a stable screen.

## Baseline workflow

In CI or scheduled runs, capture baselines once (or on approved UI changes), commit them to version control, and compare on every subsequent run with `wavexis_visual_diff`. You do not capture a separate “current” PNG for comparison — the diff tool handles live capture. Re-baseline deliberately when visual changes are intentional: overwrite the baseline file with a fresh `wavexis_screenshot`. Store baselines under a directory inside `WAVEXIS_MCP_OUTPUT_DIR` (or the current working directory) so path sandboxing accepts them.

```text
# --- Baseline capture (run once, or on approved UI change) ---
wavexis_session_open(backend="cdp", headless=true)
→ {"session_id": "abc-123"}

wavexis_navigate(session_id="abc-123", url="https://staging.example.com/login")
wavexis_wait(session_id="abc-123", strategy="selector", selector="#login-form", timeout=5000)

wavexis_screenshot(
    session_id="abc-123",
    selector="#login-form",
    full_page=false,
    output_path="./baselines/staging-login.png"
)
→ {"status": "ok", "path": "./baselines/staging-login.png", "size_bytes": 45120}

wavexis_session_close(session_id="abc-123")

# --- Regression run (every CI build) ---
wavexis_visual_diff(
    url="https://staging.example.com/login",
    baseline_path="./baselines/staging-login.png",
    selector="#login-form",
    threshold=0.1,
    output_path="./diffs/staging-login-diff.png"
)
→ {
    "status": "ok",
    "diff_percentage": 0.0,
    "diff_pixels": 0,
    "passed": true,
    "total_pixels": 38400,
    "diff_path": "./diffs/staging-login-diff.png"
}
```

Requires `--caps=data`. Session tools (`wavexis_session_open`, `wavexis_navigate`, `wavexis_wait`) are core tier.

Matching `selector` on both baseline capture and diff limits comparison to a stable component. If `total_pixels` differs from prior runs, baseline and current captures likely used different viewport, `full_page`, or `selector` settings — treat the comparison as invalid until settings match.

**When to use**: CI pipelines, scheduled regression suites, or golden-master testing where baselines are version-controlled artifacts.

## Full-page regression across deployments

`wavexis_visual_diff` has **no** `full_page` parameter — its live capture is not controlled by `wavexis_screenshot`'s `full_page` flag. For a valid compare, save the baseline with `full_page=false` (viewport-matched) so dimensions align with the live capture. If `total_pixels` differs from prior runs, treat the result as an invalid compare (mismatched capture mode), not a UI regression.

Use `wavexis_screenshot(full_page=true)` only to **archive** a full scrollable PNG for humans or external review — do not pass that file to `wavexis_visual_diff` unless `total_pixels` proves the live capture is the same size.

```text
# Baseline from production (viewport-matched for visual_diff)
wavexis_screenshot(
    url="https://production.example.com/pricing",
    full_page=false,
    wait_strategy="networkidle",
    output_path="./baselines/pricing-prod.png"
)
→ {"status": "ok", "path": "./baselines/pricing-prod.png", "size_bytes": 128000}

# Compare staging against production baseline
wavexis_visual_diff(
    url="https://staging.example.com/pricing",
    baseline_path="./baselines/pricing-prod.png",
    threshold=0.15,
    output_path="./diffs/pricing-staging-vs-prod.png"
)
→ {
    "status": "ok",
    "diff_percentage": 1.2,
    "diff_pixels": 16800,
    "passed": false,
    "total_pixels": 921600,
    "diff_path": "./diffs/pricing-staging-vs-prod.png"
}
```

Optional archival full-page capture (not for `wavexis_visual_diff`):

```text
wavexis_screenshot(
    url="https://production.example.com/pricing",
    full_page=true,
    wait_strategy="networkidle",
    output_path="./archives/pricing-prod-full.png"
)
→ {"status": "ok", "path": "./archives/pricing-prod-full.png", "size_bytes": 512000}
```

Requires `--caps=data`.

Cross-deployment diffs often fail on environment banners, feature flags, or analytics — raise `threshold` or narrow with `selector` if needed. `passed: false` with small `diff_pixels` may still be acceptable for your team; the tool uses a strict zero-diff pass rule (`passed` is true only when `diff_pixels == 0`).

**When to use**: Pre-release checks that staging matches production layout at a fixed viewport, or verifying a deploy did not alter above-the-fold content. Archive full-page PNGs separately when reviewers need the entire scrollable page.

## Multi-viewport regression

Responsive layouts must be compared at each target viewport separately. Use `wavexis_emulate_device` or `wavexis_set_viewport` in a session before both baseline capture and diff — pass the same `session_id` to `wavexis_visual_diff` so emulation persists. Create one baseline file per viewport. Re-apply the same emulation before each diff call.

```text
wavexis_session_open(backend="cdp", width=1280, height=720)
→ {"session_id": "abc-123"}

# --- Desktop baseline ---
wavexis_set_viewport(session_id="abc-123", width=1280, height=720, device_scale_factor=1)
→ {"status": "ok", "width": 1280, "height": 720, "device_scale_factor": 1}

wavexis_navigate(session_id="abc-123", url="https://example.com", wait_strategy="networkidle")
wavexis_screenshot(
    session_id="abc-123",
    full_page=false,
    output_path="./baselines/home-desktop.png"
)
→ {"status": "ok", "path": "./baselines/home-desktop.png", "size_bytes": 92000}

# --- Mobile baseline ---
wavexis_emulate_device(session_id="abc-123", device="iphone-15")
→ {"status": "ok", "device": "iphone-15"}

wavexis_navigate(session_id="abc-123", url="https://example.com", wait_strategy="networkidle")
wavexis_screenshot(
    session_id="abc-123",
    full_page=false,
    output_path="./baselines/home-mobile.png"
)
→ {"status": "ok", "path": "./baselines/home-mobile.png", "size_bytes": 65000}

# --- Regression: desktop ---
wavexis_set_viewport(session_id="abc-123", width=1280, height=720, device_scale_factor=1)
wavexis_visual_diff(
    session_id="abc-123",
    url="https://example.com",
    baseline_path="./baselines/home-desktop.png",
    output_path="./diffs/home-desktop-diff.png"
)
→ {
    "status": "ok",
    "diff_percentage": 0.0,
    "diff_pixels": 0,
    "passed": true,
    "total_pixels": 921600,
    "diff_path": "./diffs/home-desktop-diff.png"
}

# --- Regression: mobile ---
wavexis_emulate_device(session_id="abc-123", device="iphone-15")
wavexis_visual_diff(
    session_id="abc-123",
    url="https://example.com",
    baseline_path="./baselines/home-mobile.png",
    output_path="./diffs/home-mobile-diff.png"
)
→ {
    "status": "ok",
    "diff_percentage": 0.08,
    "diff_pixels": 312,
    "passed": false,
    "total_pixels": 390000,
    "diff_path": "./diffs/home-mobile-diff.png"
}

wavexis_session_close(session_id="abc-123")
```

Requires `--caps=data` and `--caps=emulation`.

A pass on desktop does not imply mobile passes. `total_pixels` should match prior runs for the same viewport preset.

**When to use**: Responsive design regression, breakpoint-specific UI tests, or CI matrices that run desktop + mobile checks.

## Tips for dynamic content

- **Wait for stability** — Call `wavexis_wait(strategy="selector")` or use `wait_strategy="networkidle"` on baseline `wavexis_screenshot` before saving. `wavexis_visual_diff` waits for `load` only (`wait_timeout` is configurable); stabilize pages before baseline capture, or use `session_id` after manual waits.
- **Hide volatile regions** — Pass the same `selector` to both `wavexis_screenshot` and `wavexis_visual_diff` (for example `#main-content`) so timestamps, ads, and avatars outside that region are ignored.
- **No built-in masking** — There is no timestamp/ad mask parameter. Narrow with `selector`, hide elements via `wavexis_eval` before capture, or raise `threshold` for noisy pages.
- **Raise tolerance** — Use `threshold=0.15`–`0.2` for anti-aliasing or font rendering variance. Default is `0.1` (range 0.0–1.0).
- **Match capture settings** — Use the same viewport/emulation and `selector` between baseline and diff. Do not pair `full_page=true` baselines with `wavexis_visual_diff` unless `total_pixels` confirms the live capture is the same size — the diff tool has no `full_page` flag, so full-page baselines usually mismatch and invalidate the compare.
- **Path sandbox** — All paths must resolve under `WAVEXIS_MCP_OUTPUT_DIR` (default: current working directory). Prefer `./baselines/` and `./diffs/` subdirectories.
- **Re-baseline intentionally** — When UI changes are approved, re-run `wavexis_screenshot` and commit updated baselines. Do not treat `passed: false` as automatically wrong.

## Response fields

| Field | Description |
|-------|-------------|
| `status` | `"ok"` on success. `"not_implemented"` if the wavexis W12 `visual_diff` action is unavailable. |
| `passed` | `true` only when `diff_pixels` is exactly `0`. Not a percentage tolerance gate. |
| `diff_pixels` | Count of pixels that differ beyond `threshold`. |
| `diff_percentage` | Share of compared pixels that differ, on a **0–100** scale (e.g. `0.03` means 0.03%). |
| `total_pixels` | Total pixels compared. Use to detect viewport/`full_page`/`selector` mismatches across runs. |
| `diff_path` | Present when `output_path` is set — path to the saved diff PNG. |
| `diff_base64` | Present when `output_path` is omitted — base64-encoded diff PNG. |
| `threshold` (input) | Float `0.0`–`1.0`, default `0.1`. Converted to a 0–255 per-channel color tolerance internally. |

On failure (missing baseline, path sandbox violation, etc.), the tool returns structured error JSON with `error`, `tool`, `type`, `message`, and `suggestion` instead of diff metrics.
