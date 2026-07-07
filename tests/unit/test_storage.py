"""Unit tests for storage tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from wavexis_mcp.models import (
    CacheStorageDeleteInput,
    CacheStorageEntriesInput,
    CacheStorageListInput,
    IndexedDBClearInput,
    IndexedDBGetDataInput,
    IndexedDBListInput,
    LocalStorageClearInput,
    LocalStorageDeleteInput,
    LocalStorageGetInput,
    LocalStorageListInput,
    LocalStorageSetInput,
    SessionStorageClearInput,
    SessionStorageDeleteInput,
    SessionStorageGetInput,
    SessionStorageListInput,
    SessionStorageSetInput,
    StorageStateRestoreInput,
    StorageStateSaveInput,
)
from wavexis_mcp.session import SessionManager

# ── LocalStorage ──


@pytest.mark.unit
async def test_localstorage_get(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(return_value="my-value")

    tool = mcp._tool_manager.get_tool("wavexis_localstorage_get")
    result = await tool.fn(LocalStorageGetInput(key="test", session_id=mock_session_id))
    data = json.loads(result)
    assert data["key"] == "test"
    assert data["value"] == "my-value"


@pytest.mark.unit
async def test_localstorage_set(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_localstorage_set")
    result = await tool.fn(
        LocalStorageSetInput(key="test", value="val", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_localstorage_delete(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_localstorage_delete")
    result = await tool.fn(LocalStorageDeleteInput(key="test", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_localstorage_clear(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_localstorage_clear")
    result = await tool.fn(LocalStorageClearInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_localstorage_list(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        return_value='{"key1": "val1", "key2": "val2"}'
    )

    tool = mcp._tool_manager.get_tool("wavexis_localstorage_list")
    result = await tool.fn(LocalStorageListInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 2
    assert data["entries"]["key1"] == "val1"


# ── SessionStorage ──


@pytest.mark.unit
async def test_sessionstorage_get(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(return_value="ss-value")

    tool = mcp._tool_manager.get_tool("wavexis_sessionstorage_get")
    result = await tool.fn(SessionStorageGetInput(key="test", session_id=mock_session_id))
    data = json.loads(result)
    assert data["value"] == "ss-value"


@pytest.mark.unit
async def test_sessionstorage_set(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_sessionstorage_set")
    result = await tool.fn(
        SessionStorageSetInput(key="test", value="val", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_sessionstorage_delete(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_sessionstorage_delete")
    result = await tool.fn(SessionStorageDeleteInput(key="test", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_sessionstorage_clear(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_sessionstorage_clear")
    result = await tool.fn(SessionStorageClearInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_sessionstorage_list(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.eval = AsyncMock(
        return_value='{"sk1": "sv1"}'
    )

    tool = mcp._tool_manager.get_tool("wavexis_sessionstorage_list")
    result = await tool.fn(SessionStorageListInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 1
    assert data["entries"]["sk1"] == "sv1"


# ── Cache Storage ──


@pytest.mark.unit
async def test_cache_storage_list(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_cache_storage_list")
    result = await tool.fn(CacheStorageListInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 2
    assert "cache1" in data["caches"]


@pytest.mark.unit
async def test_cache_storage_entries(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_cache_storage_entries")
    result = await tool.fn(
        CacheStorageEntriesInput(cache_name="cache1", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["cache_name"] == "cache1"
    assert data["count"] == 1


@pytest.mark.unit
async def test_cache_storage_delete(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_cache_storage_delete")
    result = await tool.fn(CacheStorageDeleteInput(cache_name="cache1", session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


# ── IndexedDB ──


@pytest.mark.unit
async def test_indexeddb_list(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_indexeddb_list")
    result = await tool.fn(IndexedDBListInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["count"] == 1
    assert data["databases"][0]["name"] == "db1"


@pytest.mark.unit
async def test_indexeddb_get_data(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_indexeddb_get_data")
    result = await tool.fn(
        IndexedDBGetDataInput(database="db1", store="store1", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["database"] == "db1"
    assert data["data"] == {"key": "value"}


@pytest.mark.unit
async def test_indexeddb_clear(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_indexeddb_clear")
    result = await tool.fn(
        IndexedDBClearInput(database="db1", store="store1", session_id=mock_session_id)
    )
    data = json.loads(result)
    assert data["status"] == "ok"


# ── Storage State ──


@pytest.mark.unit
async def test_storage_state_save(
    session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    backend = session_manager_with_mock.get(mock_session_id).backend
    backend.eval = AsyncMock(return_value='{"key1": "val1"}')

    out = tmp_path / "state.json"
    tool = mcp._tool_manager.get_tool("wavexis_storage_state_save")
    result = await tool.fn(StorageStateSaveInput(session_id=mock_session_id, output_path=str(out)))
    data = json.loads(result)
    assert data["path"] == str(out)
    assert data["cookies"] == 1
    assert data["localStorage_entries"] == 1
    assert out.exists()


@pytest.mark.unit
async def test_storage_state_restore(
    session_manager_with_mock: SessionManager, mock_session_id: str, tmp_path
) -> None:
    from mcp.server.fastmcp import FastMCP

    from wavexis_mcp.tools.storage import register

    mcp = FastMCP("test")
    register(mcp, session_manager_with_mock)

    state = {
        "cookies": [{"name": "c1", "value": "v1", "domain": "example.com", "path": "/"}],
        "localStorage": {"key1": "val1"},
        "sessionStorage": {"sk1": "sv1"},
    }
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(state))

    tool = mcp._tool_manager.get_tool("wavexis_storage_state_restore")
    result = await tool.fn(
        StorageStateRestoreInput(session_id=mock_session_id, input_path=str(state_path))
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["cookies_restored"] == 1
    assert data["localStorage_restored"] == 1
    assert data["sessionStorage_restored"] == 1
