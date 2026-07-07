"""Unit tests for experimental tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from wavexis_mcp.models import (
    AnimationListInput,
    AnimationPauseInput,
    AnimationPlayInput,
    AnimationSetRateInput,
    BluetoothAdapterStateInput,
    BluetoothDeviceConnectInput,
    BluetoothDeviceDisconnectInput,
    BluetoothDeviceListInput,
    CastListInput,
    CastStartInput,
    CastStopInput,
    MediaGetMessagesInput,
    MediaGetPlayersInput,
    MediaPlayerPauseInput,
    MediaPlayerPlayInput,
    MediaPlayerSeekInput,
    ServiceWorkerEmulateInput,
    ServiceWorkerListInput,
    ServiceWorkerUnregisterInput,
    ServiceWorkerUpdateInput,
    WebAudioCaptureInput,
    WebAudioStopCaptureInput,
    WebAuthnAddAuthenticatorInput,
    WebAuthnAddCredentialInput,
    WebAuthnGetCredentialInput,
    WebAuthnRemoveCredentialInput,
)
from wavexis_mcp.session import SessionManager


def _register(mcp, mgr):
    from wavexis_mcp.tools.experimental import register

    register(mcp, mgr)


# ── Service Workers (3) ──


@pytest.mark.unit
async def test_sw_list(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_service_worker_list")
    result = await tool.fn(ServiceWorkerListInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "workers" in data
    assert data["count"] == 0


@pytest.mark.unit
async def test_sw_unregister(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_service_worker_unregister")
    result = await tool.fn(
        ServiceWorkerUnregisterInput(session_id=mock_session_id, registration_id="sw-1")
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_sw_emulate(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_service_worker_emulate")
    result = await tool.fn(
        ServiceWorkerEmulateInput(
            session_id=mock_session_id, script_url="https://example.com/sw.js"
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"


# ── Animations (3) ──


@pytest.mark.unit
async def test_animation_play(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_animation_play")
    result = await tool.fn(AnimationPlayInput(session_id=mock_session_id, animation_id="anim-1"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_animation_pause(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_animation_pause")
    result = await tool.fn(AnimationPauseInput(session_id=mock_session_id, animation_id="anim-1"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_animation_set_rate(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_animation_set_rate")
    result = await tool.fn(
        AnimationSetRateInput(
            session_id=mock_session_id,
            animation_id="anim-1",
            playback_rate=2.0,
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["playback_rate"] == 2.0


# ── WebAuthn (3) ──


@pytest.mark.unit
async def test_webauthn_add_credential(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_webauthn_add_credential")
    result = await tool.fn(
        WebAuthnAddCredentialInput(
            session_id=mock_session_id,
            authenticator_id="auth-1",
            credential={"id": "cred-1", "type": "public-key"},
        )
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_webauthn_get_credential(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_webauthn_get_credential")
    result = await tool.fn(
        WebAuthnGetCredentialInput(session_id=mock_session_id, authenticator_id="auth-1")
    )
    data = json.loads(result)
    assert "credentials" in data


@pytest.mark.unit
async def test_webauthn_remove_credential(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_webauthn_remove_credential")
    result = await tool.fn(
        WebAuthnRemoveCredentialInput(session_id=mock_session_id, authenticator_id="auth-1")
    )
    data = json.loads(result)
    assert data["status"] == "ok"


# ── WebAudio (2) ──


@pytest.mark.unit
async def test_webaudio_capture(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_webaudio_capture")
    result = await tool.fn(WebAudioCaptureInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "contexts" in data


@pytest.mark.unit
async def test_webaudio_stop_capture(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_webaudio_stop_capture")
    result = await tool.fn(WebAudioStopCaptureInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


# ── Media (3) ──


@pytest.mark.unit
async def test_media_player_play(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_media_player_play")
    result = await tool.fn(MediaPlayerPlayInput(session_id=mock_session_id, player_id="p1"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_media_player_pause(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_media_player_pause")
    result = await tool.fn(MediaPlayerPauseInput(session_id=mock_session_id, player_id="p1"))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_media_player_seek(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_media_player_seek")
    result = await tool.fn(
        MediaPlayerSeekInput(session_id=mock_session_id, player_id="p1", time_ms=5000)
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["time_ms"] == 5000


# ── Cast (2) ──


@pytest.mark.unit
async def test_cast_start(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_cast_start")
    result = await tool.fn(CastStartInput(session_id=mock_session_id, sink_name="Chromecast-1"))
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["sink"] == "Chromecast-1"


@pytest.mark.unit
async def test_cast_stop(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_cast_stop")
    result = await tool.fn(CastStopInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


# ── Bluetooth (4) ──


@pytest.mark.unit
async def test_bluetooth_adapter_state(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_bluetooth_adapter_state")
    result = await tool.fn(
        BluetoothAdapterStateInput(session_id=mock_session_id, state="powered-on")
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["state"] == "powered-on"


@pytest.mark.unit
async def test_bluetooth_device_connect(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_bluetooth_device_connect")
    result = await tool.fn(
        BluetoothDeviceConnectInput(session_id=mock_session_id, name="Test Device")
    )
    data = json.loads(result)
    assert data["status"] == "ok"
    assert data["name"] == "Test Device"


@pytest.mark.unit
async def test_bluetooth_device_disconnect(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_bluetooth_device_disconnect")
    result = await tool.fn(BluetoothDeviceDisconnectInput(session_id=mock_session_id))
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_bluetooth_device_list(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_bluetooth_device_list")
    result = await tool.fn(BluetoothDeviceListInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "devices" in data


# ── New useful tools (6) ──


@pytest.mark.unit
async def test_animation_list(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.animation_list = AsyncMock(
        return_value=[{"id": "anim-1", "name": "fade", "duration": 500}]
    )

    tool = mcp._tool_manager.get_tool("wavexis_animation_list")
    result = await tool.fn(AnimationListInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "animations" in data
    assert data["count"] == 1


@pytest.mark.unit
async def test_media_get_players(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.media_get_players = AsyncMock(
        return_value=[{"id": "p1", "url": "https://example.com/video.mp4"}]
    )

    tool = mcp._tool_manager.get_tool("wavexis_media_get_players")
    result = await tool.fn(MediaGetPlayersInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "players" in data
    assert data["count"] == 1


@pytest.mark.unit
async def test_media_get_messages(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.media_get_messages = AsyncMock(
        return_value=[{"type": "error", "message": "buffering"}]
    )

    tool = mcp._tool_manager.get_tool("wavexis_media_get_messages")
    result = await tool.fn(MediaGetMessagesInput(session_id=mock_session_id, player_id="p1"))
    data = json.loads(result)
    assert "messages" in data


@pytest.mark.unit
async def test_cast_list(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    session_manager_with_mock.get(mock_session_id).backend.cast_list = AsyncMock(
        return_value=[{"name": "Chromecast-1"}]
    )

    tool = mcp._tool_manager.get_tool("wavexis_cast_list")
    result = await tool.fn(CastListInput(session_id=mock_session_id))
    data = json.loads(result)
    assert "sinks" in data
    assert data["count"] == 1


@pytest.mark.unit
async def test_sw_update(session_manager_with_mock: SessionManager, mock_session_id: str) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_service_worker_update")
    result = await tool.fn(
        ServiceWorkerUpdateInput(session_id=mock_session_id, registration_id="sw-1")
    )
    data = json.loads(result)
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_webauthn_add_virtual_authenticator(
    session_manager_with_mock: SessionManager, mock_session_id: str
) -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    _register(mcp, session_manager_with_mock)

    tool = mcp._tool_manager.get_tool("wavexis_webauthn_add_authenticator")
    result = await tool.fn(
        WebAuthnAddAuthenticatorInput(session_id=mock_session_id, protocol="ctap2", transport="usb")
    )
    data = json.loads(result)
    assert data["authenticator_id"] == "auth-1"
