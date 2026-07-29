# Python API

WaveXisMCP can be used as a Python library, not just as an MCP server. This is useful for testing, custom integrations, and embedding in other applications.

## create_server

The main entry point is `create_server()`:

```python
from wavexis_mcp.server import create_server

# Create a FastMCP instance with all 220 tools
mcp = create_server(caps="all")

# Or with specific tiers only
mcp = create_server(caps="core,network,storage")

# Run as stdio server
mcp.run()
```

### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `caps` | `str` | `"all"` | Comma-separated capability tiers |

### Returns

A `FastMCP` instance with the requested tools registered.

## Listing tools

```python
import asyncio
from wavexis_mcp.server import create_server

async def list_tools():
    mcp = create_server(caps="all")
    tools = await mcp.list_tools()
    for tool in tools:
        print(f"{tool.name}: {tool.description[:80]}")

asyncio.run(list_tools())
```

## Calling tools programmatically

```python
import asyncio
from wavexis_mcp.server import create_server

async def main():
    mcp = create_server(caps="all")
    tools = await mcp.list_tools()
    # Find the session_open tool
    session_tool = next(t for t in tools if t.name == "wavexis_session_open")
    print(f"Found: {session_tool.name}")
    print(f"Schema: {session_tool.inputSchema}")

asyncio.run(main())
```

## SessionManager

The `SessionManager` class manages browser sessions:

```python
from wavexis_mcp.session import SessionManager

sm = SessionManager()
session_id = await sm.open(backend="cdp", headless=True)
# ... use session ...
await sm.close(session_id)
```

## Models

All tool input models are Pydantic and can be imported directly:

```python
from wavexis_mcp.models import (
    SessionOpenInput,
    SessionCloseInput,
    NavigateInput,
    ScreenshotInput,
    # ... etc
)
```

## Custom server configuration

You can create a server with custom configuration:

```python
from wavexis_mcp.server import create_server

mcp = create_server(caps="core,a11y,testing")

# Access the underlying FastMCP instance
# Add your own tools, resources, or prompts
@mcp.tool()
async def my_custom_tool(query: str) -> str:
    """A custom tool added to the wavexis-mcp server."""
    return f"Result for: {query}"

mcp.run()
```

## Embedding in other applications

```python
import asyncio
from wavexis_mcp.server import create_server

async def run_embedded():
    mcp = create_server(caps="core")
    # Run with custom transport
    await mcp.run_stdio_async()

asyncio.run(run_embedded())
```
