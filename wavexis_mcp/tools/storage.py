"""Storage tools for WaveXisMCP.

Provides tools for managing localStorage, sessionStorage, Cache
Storage, IndexedDB, and composite save/restore of the full
browser storage state.
"""

from __future__ import annotations

import asyncio
import json

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
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


def _write_json(path: str, data: object) -> None:
    """Write JSON data to a file (used via ``asyncio.to_thread``).

    Args:
        path: Destination file path.
        data: JSON-serializable object to write.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _read_json(path: str) -> object:
    """Read JSON data from a file (used via ``asyncio.to_thread``).

    Args:
        path: Source file path.

    Returns:
        The deserialized JSON object.
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all storage tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    # ── LocalStorage ──

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_localstorage_get(input: LocalStorageGetInput) -> str:
        """Get a localStorage value by key.

        Args:
            input: LocalStorage get parameters.

        Returns:
            JSON string with ``key`` and ``value``.
        """
        try:
            session = session_manager.get(input.session_id)
            value = await session.backend.eval(
                f"localStorage.getItem({json.dumps(input.key)})", await_promise=False
            )
            return format_json_response({"key": input.key, "value": value})
        except Exception as e:
            return format_error("wavexis_localstorage_get", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_localstorage_set(input: LocalStorageSetInput) -> str:
        """Set a localStorage key/value pair.

        Args:
            input: LocalStorage set parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.eval(
                f"localStorage.setItem({json.dumps(input.key)}, {json.dumps(input.value)})",
                await_promise=False,
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_localstorage_set", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_localstorage_delete(input: LocalStorageDeleteInput) -> str:
        """Delete a localStorage key.

        Args:
            input: LocalStorage delete parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.eval(
                f"localStorage.removeItem({json.dumps(input.key)})", await_promise=False
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_localstorage_delete", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_localstorage_clear(input: LocalStorageClearInput) -> str:
        """Clear all localStorage entries.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.eval("localStorage.clear()", await_promise=False)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_localstorage_clear", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_localstorage_list(input: LocalStorageListInput) -> str:
        """List all localStorage entries.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with ``entries`` dict and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            raw = await session.backend.eval(
                "JSON.stringify(Object.fromEntries("
                "Array.from({length: localStorage.length}, (_, i) => "
                "[localStorage.key(i), localStorage.getItem(localStorage.key(i))])"
                "))",
                await_promise=False,
            )
            entries = json.loads(raw) if isinstance(raw, str) else raw
            return format_json_response({"entries": entries, "count": len(entries)})
        except Exception as e:
            return format_error("wavexis_localstorage_list", e)

    # ── SessionStorage ──

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_sessionstorage_get(input: SessionStorageGetInput) -> str:
        """Get a sessionStorage value by key.

        Args:
            input: SessionStorage get parameters.

        Returns:
            JSON string with ``key`` and ``value``.
        """
        try:
            session = session_manager.get(input.session_id)
            value = await session.backend.eval(
                f"sessionStorage.getItem({json.dumps(input.key)})", await_promise=False
            )
            return format_json_response({"key": input.key, "value": value})
        except Exception as e:
            return format_error("wavexis_sessionstorage_get", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_sessionstorage_set(input: SessionStorageSetInput) -> str:
        """Set a sessionStorage key/value pair.

        Args:
            input: SessionStorage set parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.eval(
                f"sessionStorage.setItem({json.dumps(input.key)}, {json.dumps(input.value)})",
                await_promise=False,
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_sessionstorage_set", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_sessionstorage_delete(input: SessionStorageDeleteInput) -> str:
        """Delete a sessionStorage key.

        Args:
            input: SessionStorage delete parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.eval(
                f"sessionStorage.removeItem({json.dumps(input.key)})",
                await_promise=False,
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_sessionstorage_delete", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_sessionstorage_clear(input: SessionStorageClearInput) -> str:
        """Clear all sessionStorage entries.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.eval("sessionStorage.clear()", await_promise=False)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_sessionstorage_clear", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_sessionstorage_list(input: SessionStorageListInput) -> str:
        """List all sessionStorage entries.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with ``entries`` dict and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            raw = await session.backend.eval(
                "JSON.stringify(Object.fromEntries("
                "Array.from({length: sessionStorage.length}, (_, i) => "
                "[sessionStorage.key(i), sessionStorage.getItem(sessionStorage.key(i))])"
                "))",
                await_promise=False,
            )
            entries = json.loads(raw) if isinstance(raw, str) else raw
            return format_json_response({"entries": entries, "count": len(entries)})
        except Exception as e:
            return format_error("wavexis_sessionstorage_list", e)

    # ── Cache Storage ──

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_cache_storage_list(input: CacheStorageListInput) -> str:
        """List all Cache Storage cache names.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with ``caches`` list and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            caches = await session.backend.cache_storage_list()
            return format_json_response({"caches": caches, "count": len(caches)})
        except Exception as e:
            return format_error("wavexis_cache_storage_list", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_cache_storage_entries(input: CacheStorageEntriesInput) -> str:
        """List entries in a Cache Storage cache.

        Args:
            input: Cache entries parameters (cache_name).

        Returns:
            JSON string with ``cache_name``, ``entries``, and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            entries = await session.backend.cache_storage_entries(input.cache_name)
            return format_json_response(
                {
                    "cache_name": input.cache_name,
                    "entries": entries,
                    "count": len(entries),
                }
            )
        except Exception as e:
            return format_error("wavexis_cache_storage_entries", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_cache_storage_delete(input: CacheStorageDeleteInput) -> str:
        """Delete a Cache Storage cache.

        Args:
            input: Cache deletion parameters (cache_name).

        Returns:
            JSON string with status ``"ok"`` and ``cache_name``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.cache_storage_delete(input.cache_name)
            return format_json_response({"status": "ok", "cache_name": input.cache_name})
        except Exception as e:
            return format_error("wavexis_cache_storage_delete", e)

    # ── IndexedDB ──

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_indexeddb_list(input: IndexedDBListInput) -> str:
        """List all IndexedDB databases and their object stores.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with ``databases`` list and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            databases = await session.backend.indexeddb_list()
            return format_json_response({"databases": databases, "count": len(databases)})
        except Exception as e:
            return format_error("wavexis_indexeddb_list", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_indexeddb_get_data(input: IndexedDBGetDataInput) -> str:
        """Get data from an IndexedDB object store.

        Args:
            input: IndexedDB query parameters (database, store, key).

        Returns:
            JSON string with ``database``, ``store``, and ``data``.
        """
        try:
            session = session_manager.get(input.session_id)
            data = await session.backend.indexeddb_get_data(input.database, input.store, input.key)
            return format_json_response(
                {
                    "database": input.database,
                    "store": input.store,
                    "data": data,
                }
            )
        except Exception as e:
            return format_error("wavexis_indexeddb_get_data", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_indexeddb_clear(input: IndexedDBClearInput) -> str:
        """Clear an IndexedDB object store.

        Args:
            input: IndexedDB clear parameters (database, store).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.indexeddb_clear(input.database, input.store)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_indexeddb_clear", e)

    # ── Storage State (composites) ──

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
    )
    async def wavexis_storage_state_save(input: StorageStateSaveInput) -> str:
        """Save cookies + localStorage + sessionStorage to a JSON file.

        Args:
            input: Save parameters (output_path).

        Returns:
            JSON string with ``path`` and entry counts.
        """
        try:
            session = session_manager.get(input.session_id)
            cookies = await session.backend.get_cookies()
            ls_raw = await session.backend.eval(
                "JSON.stringify(Object.fromEntries("
                "Array.from({length: localStorage.length}, (_, i) => "
                "[localStorage.key(i), localStorage.getItem(localStorage.key(i))])"
                "))",
                await_promise=False,
            )
            ss_raw = await session.backend.eval(
                "JSON.stringify(Object.fromEntries("
                "Array.from({length: sessionStorage.length}, (_, i) => "
                "[sessionStorage.key(i), sessionStorage.getItem(sessionStorage.key(i))])"
                "))",
                await_promise=False,
            )
            local_storage = json.loads(ls_raw) if isinstance(ls_raw, str) else ls_raw
            session_storage = json.loads(ss_raw) if isinstance(ss_raw, str) else ss_raw
            state = {
                "cookies": cookies,
                "localStorage": local_storage,
                "sessionStorage": session_storage,
            }
            await asyncio.to_thread(_write_json, input.output_path, state)
            return format_json_response(
                {
                    "path": input.output_path,
                    "cookies": len(cookies),
                    "localStorage_entries": len(local_storage),
                    "sessionStorage_entries": len(session_storage),
                }
            )
        except Exception as e:
            return format_error("wavexis_storage_state_save", e)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        )
    )
    async def wavexis_storage_state_restore(input: StorageStateRestoreInput) -> str:
        """Restore cookies + localStorage + sessionStorage from a JSON file.

        Args:
            input: Restore parameters (input_path).

        Returns:
            JSON string with status ``"ok"`` and restored entry counts.
        """
        try:
            session = session_manager.get(input.session_id)
            state = await asyncio.to_thread(_read_json, input.input_path)
            if not isinstance(state, dict):
                return format_json_response({"status": "error", "error": "Invalid state file"})

            cookies = state.get("cookies", [])
            for cookie in cookies:
                from wavexis.config import CookieParams

                await session.backend.set_cookie(
                    CookieParams(
                        name=cookie.get("name", ""),
                        value=cookie.get("value", ""),
                        domain=cookie.get("domain", ""),
                        path=cookie.get("path", "/"),
                        secure=cookie.get("secure", False),
                        http_only=cookie.get("httpOnly", False),
                    )
                )

            local_storage = state.get("localStorage", {})
            for key, value in local_storage.items():
                await session.backend.eval(
                    f"localStorage.setItem({json.dumps(key)}, {json.dumps(value)})",
                    await_promise=False,
                )

            session_storage = state.get("sessionStorage", {})
            for key, value in session_storage.items():
                await session.backend.eval(
                    f"sessionStorage.setItem({json.dumps(key)}, {json.dumps(value)})",
                    await_promise=False,
                )

            return format_json_response(
                {
                    "status": "ok",
                    "cookies_restored": len(cookies),
                    "localStorage_restored": len(local_storage),
                    "sessionStorage_restored": len(session_storage),
                }
            )
        except Exception as e:
            return format_error("wavexis_storage_state_restore", e)
