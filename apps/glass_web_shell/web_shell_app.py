from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import time
import webbrowser
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from forgeos.shared.pyside6_glass.integration import (  # noqa: E402
    LocalHttpIntegrationAdapter,
    LocalHttpIntegrationConfig,
    create_reference_workspace_service,
)


WEB_ROOT = Path(__file__).resolve().parent / "web"


def _content_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    return guessed or "application/octet-stream"


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=True).encode("utf-8")


def _read_json_response(url: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    body = _json_bytes(payload or {}) if method.upper() == "POST" else None
    request = Request(
        url=url,
        method=method.upper(),
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=3.0) as response:  # noqa: S310 - local-only shell
            status = int(getattr(response, "status", 200))
            raw = response.read().decode("utf-8")
            data = json.loads(raw) if raw else {}
            return status, data
    except HTTPError as exc:
        raw = exc.read().decode("utf-8") if exc.fp else ""
        try:
            data = json.loads(raw) if raw else {}
        except Exception:  # noqa: BLE001
            data = {"ok": False, "kind": "error", "error": {"message": raw or str(exc)}}
        return int(exc.code), data


def _proxy_request(
    upstream_base: str,
    path: str,
    method: str,
    payload: bytes | None,
) -> tuple[int, bytes, str]:
    request = Request(
        url=f"{upstream_base}{path}",
        method=method.upper(),
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=4.0) as response:  # noqa: S310 - local-only proxy
            return (
                int(getattr(response, "status", 200)),
                response.read(),
                str(response.headers.get("Content-Type", "application/json; charset=utf-8")),
            )
    except HTTPError as exc:
        body = exc.read() if exc.fp else _json_bytes({"ok": False, "kind": "error", "error": {"message": str(exc)}})
        return int(exc.code), body, str(exc.headers.get("Content-Type", "application/json; charset=utf-8"))
    except URLError as exc:
        body = _json_bytes(
            {
                "ok": False,
                "kind": "error",
                "error": {"code": "upstream_unreachable", "message": str(exc.reason)},
            }
        )
        return 502, body, "application/json; charset=utf-8"


def _safe_static_path(raw_path: str) -> Path | None:
    path = raw_path.split("?", 1)[0].split("#", 1)[0]
    if path in {"", "/"}:
        return WEB_ROOT / "index.html"
    relative = path.lstrip("/")
    target = (WEB_ROOT / relative).resolve()
    if WEB_ROOT.resolve() not in target.parents and target != WEB_ROOT.resolve():
        return None
    return target


def _make_handler(upstream_base: str):
    class _ShellHandler(BaseHTTPRequestHandler):
        server_version = "GlassWebShell/1.0"

        def do_GET(self) -> None:  # noqa: N802
            if self.path.startswith("/api/"):
                self._handle_proxy()
                return
            if self.path == "/config.json":
                self._write_json(
                    200,
                    {
                        "ok": True,
                        "kind": "web_shell_config",
                        "api_base": "/api/v1",
                        "features": {
                            "events_polling": True,
                            "event_stream_scaffold": True,
                        },
                    },
                )
                return
            self._serve_static()

        def do_POST(self) -> None:  # noqa: N802
            if self.path.startswith("/api/"):
                self._handle_proxy()
                return
            self._write_json(
                404,
                {
                    "ok": False,
                    "kind": "error",
                    "error": {
                        "code": "route_not_found",
                        "message": f"unsupported route '{self.path}'",
                        "status_code": 404,
                    },
                },
            )

        def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
            return

        def _handle_proxy(self) -> None:
            proxied_path = self.path[len("/api") :]
            payload = None
            if self.command.upper() == "POST":
                length = int(self.headers.get("Content-Length") or "0")
                payload = self.rfile.read(length) if length > 0 else _json_bytes({})
            status, body, content_type = _proxy_request(upstream_base, proxied_path, self.command, payload)
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _serve_static(self) -> None:
            target = _safe_static_path(self.path)
            if target is None or not target.exists() or not target.is_file():
                target = WEB_ROOT / "index.html"
            data = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", _content_type(target))
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _write_json(self, status: int, payload: dict[str, Any]) -> None:
            data = _json_bytes(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return _ShellHandler


@dataclass(slots=True)
class WebShellRuntime:
    host: str = "127.0.0.1"
    port: int = 3184
    open_browser: bool = False
    service: Any = field(init=False)
    reference_state: Any = field(init=False)
    integration_adapter: LocalHttpIntegrationAdapter = field(init=False)
    web_server: ThreadingHTTPServer | None = field(init=False, default=None)
    web_thread: Thread | None = field(init=False, default=None)
    api_base_url: str = field(init=False, default="")
    web_base_url: str = field(init=False, default="")

    def __post_init__(self) -> None:
        self.service, self.reference_state = create_reference_workspace_service(debug=False, namespace="workspace")
        self.integration_adapter = LocalHttpIntegrationAdapter(
            self.service,
            LocalHttpIntegrationConfig(host="127.0.0.1", port=0, debug=False),
        )

    def start(self) -> str:
        self.api_base_url = self.integration_adapter.start()
        handler = _make_handler(self.api_base_url)
        self.web_server = ThreadingHTTPServer((self.host, int(self.port)), handler)
        self.web_thread = Thread(target=self.web_server.serve_forever, name="glass-web-shell", daemon=True)
        self.web_thread.start()
        host, port = self.web_server.server_address
        self.web_base_url = f"http://{host}:{port}"
        if self.open_browser:
            webbrowser.open(self.web_base_url)
        return self.web_base_url

    def stop(self) -> None:
        if self.web_server is not None:
            self.web_server.shutdown()
            self.web_server.server_close()
            self.web_server = None
        if self.web_thread is not None:
            self.web_thread.join(timeout=1.0)
            self.web_thread = None
        self.integration_adapter.stop()


def run_smoke_check() -> int:
    runtime = WebShellRuntime(host="127.0.0.1", port=0, open_browser=False)
    runtime.start()
    try:
        status_health, payload_health = _read_json_response(f"{runtime.web_base_url}/api/v1/health")
        if status_health != 200 or not bool(payload_health.get("ok")):
            raise RuntimeError("health check failed")

        status_snapshot, payload_snapshot = _read_json_response(
            f"{runtime.web_base_url}/api/v1/snapshot",
            method="POST",
            payload={"snapshot_id": "workspace", "context": {"client_id": "smoke-client"}},
        )
        if status_snapshot != 200 or not bool(payload_snapshot.get("ok")):
            raise RuntimeError("snapshot request failed")

        status_query, payload_query = _read_json_response(
            f"{runtime.web_base_url}/api/v1/query",
            method="POST",
            payload={
                "query": "workspace.summary.get",
                "params": {},
                "context": {"client_id": "smoke-client"},
            },
        )
        if status_query != 200 or not bool(payload_query.get("ok")):
            raise RuntimeError("query request failed")

        status_command, payload_command = _read_json_response(
            f"{runtime.web_base_url}/api/v1/command",
            method="POST",
            payload={
                "command": "workspace.item.upsert",
                "payload": {"item_id": "smoke-item", "item": {"label": "Smoke Item"}},
                "context": {"client_id": "smoke-client", "capabilities": ["workspace.write"]},
                "idempotency_key": "smoke-item-upsert",
            },
        )
        if status_command != 200 or not bool(payload_command.get("ok")):
            raise RuntimeError("command request failed")

        status_events, payload_events = _read_json_response(f"{runtime.web_base_url}/api/v1/events?since=0&limit=10")
        if status_events != 200 or not bool(payload_events.get("ok")):
            raise RuntimeError("events request failed")

        status_contracts, payload_contracts = _read_json_response(f"{runtime.web_base_url}/api/v1/contracts")
        if status_contracts != 200 or not bool(payload_contracts.get("ok")):
            raise RuntimeError("contracts request failed")

        print(
            "SMOKE_OK",
            json.dumps(
                {
                    "health": payload_health.get("kind"),
                    "snapshot": payload_snapshot.get("kind"),
                    "query": payload_query.get("kind"),
                    "command": payload_command.get("kind"),
                    "events": len(payload_events.get("events") or []),
                    "contracts": bool(payload_contracts.get("endpoints")),
                },
                ensure_ascii=True,
            ),
        )
        return 0
    finally:
        runtime.stop()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run neutral lightweight web shell for integration boundary.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3184)
    parser.add_argument("--open-browser", action="store_true")
    parser.add_argument("--smoke", action="store_true", help="Run quick end-to-end shell smoke check and exit.")
    args = parser.parse_args()

    if args.smoke:
        return run_smoke_check()

    runtime = WebShellRuntime(host=args.host, port=args.port, open_browser=args.open_browser)
    url = runtime.start()
    print(f"[Glass Web Shell] Web UI: {url}")
    print(f"[Glass Web Shell] Integration API upstream: {runtime.api_base_url}")
    print("[Glass Web Shell] Press Ctrl+C to stop.")
    try:
        while True:
            if runtime.web_thread is not None and not runtime.web_thread.is_alive():
                raise RuntimeError("web shell thread stopped unexpectedly")
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        runtime.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
