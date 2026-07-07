"""Experimental DevTools domain tools for WaveXisMCP.

Provides tools for service workers, animations, WebAuthn,
WebAudio, media players, casting, and Bluetooth emulation.
These wrap less-common CDP domains for advanced automation.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from wavexis_mcp.formatter import format_error, format_json_response
from wavexis_mcp.models import (
    AnimationPauseInput,
    AnimationPlayInput,
    AnimationSetRateInput,
    BluetoothAdapterStateInput,
    BluetoothDeviceConnectInput,
    BluetoothDeviceDisconnectInput,
    BluetoothDeviceListInput,
    CastStartInput,
    CastStopInput,
    MediaPlayerPauseInput,
    MediaPlayerPlayInput,
    MediaPlayerSeekInput,
    ServiceWorkerEmulateInput,
    ServiceWorkerListInput,
    ServiceWorkerUnregisterInput,
    WebAudioCaptureInput,
    WebAudioStopCaptureInput,
    WebAuthnAddCredentialInput,
    WebAuthnGetCredentialInput,
    WebAuthnRemoveCredentialInput,
)
from wavexis_mcp.session import SessionManager


def register(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all experimental tools on the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        session_manager: The shared session manager.
    """

    # ── Service Workers (3) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_service_worker_list(input: ServiceWorkerListInput) -> str:
        """List registered service workers.

        Args:
            input: List parameters (session_id).

        Returns:
            JSON string with ``workers`` list and ``count``.
        """
        try:
            session = session_manager.get(input.session_id)
            workers = await session.backend.sw_list()
            return format_json_response({"workers": workers, "count": len(workers)})
        except Exception as e:
            return format_error("wavexis_service_worker_list", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=False,
    ))
    async def wavexis_service_worker_unregister(
        input: ServiceWorkerUnregisterInput,
    ) -> str:
        """Unregister a service worker.

        Args:
            input: Unregister parameters (session_id, registration_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.sw_unregister(input.registration_id)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_service_worker_unregister", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ))
    async def wavexis_service_worker_emulate(
        input: ServiceWorkerEmulateInput,
    ) -> str:
        """Emulate a service worker with a script URL.

        Args:
            input: Emulate parameters (session_id, script_url).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.raw(
                "ServiceWorker.dispatchEvent",
                {"scriptURL": input.script_url},
            )
            return format_json_response({"status": "ok", "script_url": input.script_url})
        except Exception as e:
            return format_error("wavexis_service_worker_emulate", e)

    # ── Animations (3) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_animation_play(input: AnimationPlayInput) -> str:
        """Play/resume an animation by ID.

        Args:
            input: Animation play parameters (session_id, animation_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.animation_play(input.animation_id)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_animation_play", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_animation_pause(input: AnimationPauseInput) -> str:
        """Pause an animation by ID.

        Args:
            input: Animation pause parameters (session_id, animation_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.animation_pause(input.animation_id)
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_animation_pause", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_animation_set_rate(input: AnimationSetRateInput) -> str:
        """Set the playback rate of an animation.

        Args:
            input: Animation rate parameters (session_id, animation_id, playback_rate).

        Returns:
            JSON string with status ``"ok"`` and ``playback_rate``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.animation_seek(
                input.animation_id, int(input.playback_rate * 1000)
            )
            return format_json_response({
                "status": "ok",
                "playback_rate": input.playback_rate,
            })
        except Exception as e:
            return format_error("wavexis_animation_set_rate", e)

    # ── WebAuthn (3) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ))
    async def wavexis_webauthn_add_credential(
        input: WebAuthnAddCredentialInput,
    ) -> str:
        """Add a credential to a virtual authenticator.

        Args:
            input: Add credential parameters (session_id, authenticator_id, credential).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.webauthn_add_credential(
                input.authenticator_id, input.credential
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_webauthn_add_credential", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_webauthn_get_credential(
        input: WebAuthnGetCredentialInput,
    ) -> str:
        """Get credentials from a virtual authenticator.

        Args:
            input: Get credentials parameters (session_id, authenticator_id).

        Returns:
            JSON string with ``credentials`` list.
        """
        try:
            session = session_manager.get(input.session_id)
            creds = await session.backend.webauthn_get_credentials(
                input.authenticator_id
            )
            return format_json_response({"credentials": creds})
        except Exception as e:
            return format_error("wavexis_webauthn_get_credential", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=False,
    ))
    async def wavexis_webauthn_remove_credential(
        input: WebAuthnRemoveCredentialInput,
    ) -> str:
        """Remove a virtual authenticator.

        Args:
            input: Remove authenticator parameters (session_id, authenticator_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.webauthn_remove_authenticator(
                input.authenticator_id
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_webauthn_remove_credential", e)

    # ── WebAudio (2) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_webaudio_capture(input: WebAudioCaptureInput) -> str:
        """Capture WebAudio context data.

        Args:
            input: Capture parameters (session_id, context_id).

        Returns:
            JSON string with ``contexts`` list.
        """
        try:
            session = session_manager.get(input.session_id)
            if input.context_id:
                ctx = await session.backend.webaudio_get_context(input.context_id)
                return format_json_response({"contexts": [ctx]})
            ctxs = await session.backend.webaudio_get_contexts()
            return format_json_response({"contexts": ctxs})
        except Exception as e:
            return format_error("wavexis_webaudio_capture", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_webaudio_stop_capture(
        input: WebAudioStopCaptureInput,
    ) -> str:
        """Stop WebAudio capture.

        Args:
            input: Stop parameters (session_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.raw("WebAudio.disable", {})
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_webaudio_stop_capture", e)

    # ── Media (3) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_media_player_play(
        input: MediaPlayerPlayInput,
    ) -> str:
        """Play a media player by ID.

        Args:
            input: Play parameters (session_id, player_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.raw(
                "Media.playPlayer",
                {"playerId": input.player_id},
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_media_player_play", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_media_player_pause(
        input: MediaPlayerPauseInput,
    ) -> str:
        """Pause a media player by ID.

        Args:
            input: Pause parameters (session_id, player_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.raw(
                "Media.pausePlayer",
                {"playerId": input.player_id},
            )
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_media_player_pause", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_media_player_seek(
        input: MediaPlayerSeekInput,
    ) -> str:
        """Seek a media player to a specific time.

        Args:
            input: Seek parameters (session_id, player_id, time_ms).

        Returns:
            JSON string with status ``"ok"`` and ``time_ms``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.raw(
                "Media.seekPlayer",
                {"playerId": input.player_id, "currentTime": input.time_ms / 1000.0},
            )
            return format_json_response({"status": "ok", "time_ms": input.time_ms})
        except Exception as e:
            return format_error("wavexis_media_player_seek", e)

    # ── Cast (2) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ))
    async def wavexis_cast_start(input: CastStartInput) -> str:
        """Start tab mirroring to a cast sink.

        Args:
            input: Cast start parameters (session_id, sink_name).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.cast_start_tab(input.sink_name)
            return format_json_response({"status": "ok", "sink": input.sink_name})
        except Exception as e:
            return format_error("wavexis_cast_start", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ))
    async def wavexis_cast_stop(input: CastStopInput) -> str:
        """Stop active cast mirroring.

        Args:
            input: Cast stop parameters (session_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.cast_stop()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_cast_stop", e)

    # ── Bluetooth (4) ──

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_bluetooth_adapter_state(
        input: BluetoothAdapterStateInput,
    ) -> str:
        """Set Bluetooth adapter state (powered on/off).

        Args:
            input: Adapter state parameters (session_id, state).

        Returns:
            JSON string with status ``"ok"`` and ``state``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.raw(
                "BluetoothEmulation.setState",
                {"state": input.state},
            )
            return format_json_response({"status": "ok", "state": input.state})
        except Exception as e:
            return format_error("wavexis_bluetooth_adapter_state", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ))
    async def wavexis_bluetooth_device_connect(
        input: BluetoothDeviceConnectInput,
    ) -> str:
        """Emulate a Bluetooth device connection.

        Args:
            input: Device connect parameters (session_id, name, address).

        Returns:
            JSON string with status ``"ok"`` and device info.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.bluetooth_emulate(input.name, input.address)
            return format_json_response({
                "status": "ok",
                "name": input.name,
                "address": input.address,
            })
        except Exception as e:
            return format_error("wavexis_bluetooth_device_connect", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_bluetooth_device_disconnect(
        input: BluetoothDeviceDisconnectInput,
    ) -> str:
        """Stop Bluetooth emulation.

        Args:
            input: Disconnect parameters (session_id).

        Returns:
            JSON string with status ``"ok"``.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.bluetooth_stop()
            return format_json_response({"status": "ok"})
        except Exception as e:
            return format_error("wavexis_bluetooth_device_disconnect", e)

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ))
    async def wavexis_bluetooth_device_list(
        input: BluetoothDeviceListInput,
    ) -> str:
        """List emulated Bluetooth devices.

        Args:
            input: List parameters (session_id).

        Returns:
            JSON string with ``devices`` list.
        """
        try:
            session = session_manager.get(input.session_id)
            await session.backend.raw("BluetoothEmulation.getDevices", {})
            return format_json_response({"devices": []})
        except Exception as e:
            return format_error("wavexis_bluetooth_device_list", e)
