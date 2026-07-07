"""Interaction tools for WaveXisMCP.

Provides tools for handling JavaScript dialogs, intercepting
downloads, and managing browser permissions.
"""

from __future__ import annotations

import asyncio
import os

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import encode_base64, format_error, format_json_response
from wavexis_mcp.models import (
    DialogAcceptInput,
    DialogDismissInput,
    GrantPermissionInput,
    InterceptDownloadInput,
    ResetPermissionsInput,
)
from wavexis_mcp.session import SessionManager


def _write_bytes(path: str, data: bytes) -> None:
    """Write bytes to a file (used via ``asyncio.to_thread``).

    Args:
        path: Destination file path.
        data: Raw bytes to write.
    """
    with open(path, "wb") as f:
        f.write(data)


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all interaction tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_dialog_accept(input: DialogAcceptInput) -> str:
        """Accept a JavaScript dialog (alert, confirm, prompt).

        Args:
            input: Dialog accept parameters (prompt_text).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.dialog_accept(input.prompt_text)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_dialog_accept", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_dialog_dismiss(input: DialogDismissInput) -> str:
        """Dismiss a JavaScript dialog.

        Args:
            input: Dialog dismiss parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.dialog_dismiss()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_dialog_dismiss", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_intercept_download(input: InterceptDownloadInput) -> str:
        """Intercept a download matching a URL pattern.

        Args:
            input: Download interception parameters (pattern, output_path).

        Returns:
            JSON string with file path or base64 data and size.
        """
        try:
            session = session_manager.get(input.session_id)
            data = await session.backend.intercept_download(input.pattern)
            if input.output_path:
                await asyncio.to_thread(_write_bytes, input.output_path, data)
                return format_json_response({
                    "path": input.output_path,
                    "size_bytes": len(data),
                })
            return format_json_response({
                "status": "ok",
                "filename": os.path.basename(input.pattern),
                "size_bytes": len(data),
                "base64": encode_base64(data),
            })
        except Exception as e:
            return format_error("wavexis_intercept_download", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_grant_permission(input: GrantPermissionInput) -> str:
        """Grant a browser permission (geolocation, notifications, etc.).

        Args:
            input: Permission parameters.

        Returns:
            JSON string with status ``"ok"`` and ``permission``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.grant_permission(input.permission)
            return format_json_response({"status": "ok", "permission": input.permission})
        except Exception as e:
            return format_error("wavexis_grant_permission", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_reset_permissions(input: ResetPermissionsInput) -> str:
        """Reset all granted permissions.

        Args:
            input: Session reference parameters.

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.reset_permissions()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_reset_permissions", e)
