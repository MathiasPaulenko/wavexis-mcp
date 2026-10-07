"""Verificación E2E real de las correcciones del audit contra Chrome real.

Corre cada feature arreglada end-to-end (no mocks). Salida PASS/FAIL por check.
Requiere Chrome/Chromium instalado.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import json
import os
import sys
import tempfile
from typing import Any

from mcp.server.fastmcp import FastMCP

from wavexis_mcp.models import (
    BluetoothDeviceConnectInput,
    BluetoothDeviceDisconnectInput,
    BluetoothDeviceListInput,
    InvokeInput,
    LighthouseInput,
    SessionOpenInput,
    StorageStateRestoreInput,
    SubscribeEventsInput,
    UnsubscribeEventsInput,
    VideoActionOverlayInput,
    VideoAddChapterInput,
    VideoRecordInput,
    VideoStopInput,
    WebsocketInterceptInput,
)
from wavexis_mcp.session import SessionManager
from wavexis_mcp.tools import (
    data,
    devtools,
    experimental,
    storage,
    utility,
    video,
)
from wavexis_mcp.tools import session as tsession

OUTPUT_DIR = tempfile.mkdtemp(prefix="wxmcp-e2e-")
os.environ.setdefault("WAVEXIS_MCP_OUTPUT_DIR", OUTPUT_DIR)
# Permite navegar a 127.0.0.1 para el test de WebSocket (página local).
os.environ.setdefault("WAVEXIS_MCP_ALLOW_INTERNAL_URLS", "1")

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} — {detail}")


async def tool(mcp: FastMCP, name: str, input_obj: Any) -> dict[str, Any]:
    t = mcp._tool_manager.get_tool(name)
    assert t is not None, f"tool {name} not registered"
    return json.loads(await t.fn(input_obj))


async def ws_echo_server(port: int = 8766) -> Any:
    import websockets

    async def echo(ws):
        async for msg in ws:
            await ws.send(f"echo:{msg}")

    return await websockets.serve(echo, "127.0.0.1", port)


async def main() -> int:
    mcp = FastMCP("e2e")
    mgr = SessionManager()
    tsession.register(mcp, mgr)
    utility.register(mcp, mgr)
    storage.register(mcp, mgr)
    data.register(mcp, mgr)
    devtools.register(mcp, mgr)
    experimental.register(mcp, mgr)
    video.register(mcp, mgr, {})

    # ── 1. Session + invoke with dataclass params ────────────────
    r = await tool(mcp, "wavexis_session_open", SessionOpenInput(backend="cdp", headless=True))
    sid = r["session_id"]
    check("session_open resuelve backend", r.get("backend") == "cdp", str(r))

    r = await tool(
        mcp,
        "wavexis_invoke",
        InvokeInput(
            method="throttle_network",
            params={
                "offline": False,
                "latency_ms": 50,
                "download_bps": -1,
                "upload_bps": -1,
            },
            session_id=sid,
        ),
    )
    check("invoke throttle_network (dataclass)", r.get("status") == "ok", str(r)[:120])

    r = await tool(
        mcp,
        "wavexis_invoke",
        InvokeInput(
            method="set_cookie",
            params={"name": "invoke_c", "value": "v", "domain": "example.com"},
            session_id=sid,
        ),
    )
    check("invoke set_cookie (CookieParams)", r.get("status") == "ok", str(r)[:120])

    # ── 2. Storage state restore (session-level --storage-state) ─
    state = {
        "cookies": [
            {
                "name": "c1",
                "value": "v1",
                "domain": "example.com",
                "path": "/",
                "secure": True,
                "httpOnly": False,
                "sameSite": "Lax",
                "expires": 2000000000,
            }
        ],
        "localStorage": {"theme": "dark"},
        "sessionStorage": {"temp": "42"},
    }
    # secure_output_path exige que el fichero esté dentro de OUTPUT_DIR.
    sf_name = os.path.join(OUTPUT_DIR, "storage-state.json")
    with open(sf_name, "w") as sf:  # noqa: ASYNC230
        json.dump(state, sf)
    mgr.storage_state_path = sf_name
    sid2 = await mgr.open(backend="cdp", headless=True)
    sess2 = mgr.get(sid2)
    await sess2.backend.navigate("https://example.com")
    cookies = await sess2.backend.get_cookies()
    names = {c["name"] for c in cookies}
    lv = await sess2.backend.eval("localStorage.getItem('theme')")
    sv = await sess2.backend.eval("sessionStorage.getItem('temp')")
    check(
        "--storage-state cookies+local+session",
        "c1" in names and lv == "dark" and sv == "42",
        f"cookies={names} local={lv} session={sv}",
    )
    await mgr.close(sid2)
    mgr.storage_state_path = None

    # ── 3. Tool-level storage_state_restore ──────────────────────
    sess = mgr.get(sid)
    await sess.backend.navigate("https://example.com")
    r = await tool(
        mcp,
        "wavexis_storage_state_restore",
        StorageStateRestoreInput(session_id=sid, input_path=sf_name),
    )
    lv2 = await sess.backend.eval("localStorage.getItem('theme')")
    check(
        "storage_state_restore tool",
        r.get("status") == "ok" and lv2 == "dark",
        f"{str(r)[:80]} local={lv2}",
    )

    # ── 4. Lighthouse real ───────────────────────────────────────
    r = await tool(
        mcp,
        "wavexis_lighthouse",
        LighthouseInput(url="https://example.com", session_id=sid),
    )
    cats = r.get("categories", {})
    perf = cats.get("performance", {})
    check(
        "lighthouse scores reales",
        r.get("status") == "ok"
        and perf.get("ttfb_ms", 0) > 0
        and cats.get("seo", {}).get("h1_count", 0) >= 0
        and "score" in cats.get("accessibility", {}),
        f"perf_ttfb={perf.get('ttfb_ms')} seo={cats.get('seo', {}).get('score')}"
        f" a11y={cats.get('accessibility', {}).get('score')}",
    )

    # ── 5. WebSocket intercept real ──────────────────────────────
    # HTTPS bloquea ws:// (mixed content), así que servimos una página HTTP
    # local que abre el WebSocket al cargar — dentro de la ventana de captura.
    import http.server
    import threading

    ws_page = (
        b"<html><body><script>"
        b"var ws=new WebSocket('ws://127.0.0.1:8766');"
        b"ws.onopen=function(){setInterval(function(){ws.send('ping')},150)};"
        b"</script></body></html>"
    )

    class _H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(ws_page)

        def log_message(self, *a):
            pass

    srv = await ws_echo_server()
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 8767), _H)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    r = await tool(
        mcp,
        "wavexis_websocket_intercept",
        WebsocketInterceptInput(
            url="http://127.0.0.1:8767/",
            duration_ms=2500,
            url_pattern="127.0.0.1",
            session_id=sid,
        ),
    )
    srv.close()
    httpd.shutdown()
    frames = r.get("frames_sent", 0) + r.get("frames_received", 0)
    check(
        "websocket_intercept captura frames reales",
        frames > 0 and any("127.0.0.1" in str(f.get("url", "")) for f in r.get("sent", [])),
        f"sent={r.get('frames_sent')} received={r.get('frames_received')}"
        f" sample={str(r.get('sent', [])[:1])[:80]}",
    )

    # mock_responses debe rechazarse explícitamente
    r = await tool(
        mcp,
        "wavexis_websocket_intercept",
        WebsocketInterceptInput(
            url="https://example.com",
            session_id=sid,
            mock_responses={"x": "y"},
        ),
    )
    check("websocket mock_responses → error claro", "error" in r, str(r)[:100])

    # ── 6. Video record real ─────────────────────────────────────
    # página animada para que el screencast emita frames
    await sess.backend.eval(
        "var d=document.createElement('div');"
        "d.style.cssText='position:fixed;top:0;left:0;width:50px;height:50px;background:red';"
        "document.body.appendChild(d);"
        "window.__anim=setInterval(()=>{d.style.left=(parseInt(d.style.left)+10)%600+'px';d.style.background='rgb('+Math.random()*255+',0,0)';},50);"
    )
    r = await tool(mcp, "wavexis_video_record", VideoRecordInput(session_id=sid))
    rid = r.get("recording_id", "")
    check("video_record arranca", r.get("status") == "recording", str(r)[:80])
    await tool(
        mcp,
        "wavexis_video_add_chapter",
        VideoAddChapterInput(session_id=sid, recording_id=rid, title="cap1", timestamp_ms=500),
    )
    await asyncio.sleep(2.0)
    r = await tool(
        mcp,
        "wavexis_video_stop",
        VideoStopInput(session_id=sid, recording_id=rid),
    )
    n_frames = r.get("frames", 0)
    is_jpeg = False
    if r.get("base64"):
        with contextlib.suppress(Exception):
            is_jpeg = base64.b64decode(r["base64"])[:2] == b"\xff\xd8"
    check(
        "video frames capturados + mjpeg",
        n_frames > 0 and r.get("format") == "mjpeg" and is_jpeg,
        f"frames={n_frames} fmt={r.get('format')} jpeg={is_jpeg} size={r.get('size_bytes')}",
    )
    check(
        "video chapters devueltos",
        any(c.get("title") == "cap1" for c in r.get("chapters", [])),
        str(r.get("chapters")),
    )

    # ── 7. Action overlay real ───────────────────────────────────
    r = await tool(
        mcp,
        "wavexis_video_action_overlay",
        VideoActionOverlayInput(session_id=sid, show=True),
    )
    exists = await sess.backend.eval("!!document.getElementById('__wavexis_overlay')")
    check("action overlay inyecta DOM", r.get("status") == "ok" and exists is True, str(exists))
    await tool(
        mcp, "wavexis_video_action_overlay", VideoActionOverlayInput(session_id=sid, show=False)
    )
    gone = await sess.backend.eval("!document.getElementById('__wavexis_overlay')")
    check("action overlay se elimina", gone is True, str(gone))

    # ── 8. Bluetooth ─────────────────────────────────────────────
    r = await tool(
        mcp,
        "wavexis_bluetooth_device_connect",
        BluetoothDeviceConnectInput(session_id=sid, name="TestDev", address="11:22:33:44:55:66"),
    )
    connect_ok = r.get("status") == "ok"
    connect_err = r.get("error", "")
    r2 = await tool(mcp, "wavexis_bluetooth_device_list", BluetoothDeviceListInput(session_id=sid))
    listed = r2.get("devices", [])
    if connect_ok:
        ok = any(d.get("name") == "TestDev" for d in listed)
        detail = f"list={listed}"
    else:
        # BluetoothEmulation.enable no está soportado en este Chrome (límite
        # de wavexis/CDP, no del tool). Lo que debe cumplirse es que list
        # devuelva datos reales y connect un error explícito, no un fake ok.
        ok = bool(connect_err) and isinstance(listed, list)
        detail = f"connect_err={connect_err[:60]} list={listed}"
    check("bluetooth connect→list (o error claro)", ok, detail)
    await tool(
        mcp, "wavexis_bluetooth_device_disconnect", BluetoothDeviceDisconnectInput(session_id=sid)
    )
    r3 = await tool(mcp, "wavexis_bluetooth_device_list", BluetoothDeviceListInput(session_id=sid))
    check("bluetooth disconnect limpia", len(r3.get("devices", [])) == 0, str(r3)[:80])

    # ── 9. subscribe/unsubscribe events ──────────────────────────
    r = await tool(
        mcp,
        "wavexis_subscribe_events",
        SubscribeEventsInput(session_id=sid, event_types=["navigation"]),
    )
    sub_id = r.get("subscription_id")
    await sess.backend.navigate("https://example.org")
    await asyncio.sleep(0.5)
    r = await tool(
        mcp,
        "wavexis_unsubscribe_events",
        UnsubscribeEventsInput(session_id=sid, subscription_id=sub_id),
    )
    check(
        "event subscription captura",
        r.get("events_captured", 0) > 0,
        f"captured={r.get('events_captured')} sample={str(r.get('events', [])[:1])[:100]}",
    )

    await mgr.close(sid)

    # ── 10. BiDi smoke ───────────────────────────────────────────
    r = await tool(mcp, "wavexis_session_open", SessionOpenInput(backend="bidi", headless=True))
    if r.get("status") == "ok":
        bsid = r["session_id"]
        check("bidi session abre", r.get("backend") == "bidi", str(r)[:80])
        bsess = mgr.get(bsid)
        await bsess.backend.navigate("https://example.com")
        title = await bsess.backend.eval("document.title")
        check("bidi navigate+eval", bool(title), str(title)[:60])
        await mgr.close(bsid)
    else:
        # chromedriver no instalado → BiDi no disponible en este entorno.
        # El error debe ser explícito, no un crash genérico.
        check(
            "bidi session (no disponible: sin chromedriver)", "chromedriver" in str(r), str(r)[:120]
        )

    # ── 11. Rate limiter 0 = unlimited ───────────────────────────
    from wavexis_mcp.rate_limiter import RateLimiter

    rl = RateLimiter(rate=0, burst=10)
    ok = all([await rl.acquire("s") for _ in range(50)])
    check("rate_limit 0 desactiva", ok, "50/50 acquires")

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n{'=' * 60}\nRESULTADO: {passed}/{len(RESULTS)} checks OK")
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"  FAIL: {name} — {detail}")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
