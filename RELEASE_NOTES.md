# Release v1.6.5

## Bug Fixes

### a11y_snapshot: CDP flat node tree parsing
- **Problem**: `wavexis_a11y_snapshot` returned only 1 element with `role: unknown`
- **Cause**: CDP's `Accessibility.getFullAXTree` returns a flat list of nodes with `nodeId`/`parentId` references, but the MCP code expected a pre-built tree with `role` (string), `name` (string), and `children` (list)
- **Fix**: Added `_build_a11y_tree()` to transform CDP flat node list into nested tree structure with proper role/name extraction from CDP dict format

### Backend timeouts to prevent hanging tools
- **Problem**: Tools like `list_tabs`, `screenshot` (with `output_path`), and `session_info` hung indefinitely after extended use
- **Cause**: No timeout on backend WebSocket calls — if the browser connection degrades, `await` hangs forever
- **Fix**: Added `SessionManager.call_backend()` with `asyncio.wait_for()` (30s default timeout). Applied to `tabs.py`, `capture.py`, `a11y.py`, `session.py`, and `server.py` (act tool)

### assert_url: case-insensitive matching
- **Problem**: `wavexis_assert_url` failed matching "python" against "Python" in URLs
- **Fix**: Changed to case-insensitive substring matching
