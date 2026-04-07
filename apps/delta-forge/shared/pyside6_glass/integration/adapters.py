from __future__ import annotations

import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any, Mapping
from urllib.parse import parse_qs, urlparse

from .contracts import IntegrationResponse
from .service import IntegrationService


def _json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=True).encode("utf-8")


class InProcessIntegrationAdapter:
    """Lightweight adapter for tests/tools that call integration service in-process."""

    def __init__(self, service: IntegrationService) -> None:
        self.service = service

    def command(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.service.dispatch_command(payload).to_payload()

    def query(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.service.dispatch_query(payload).to_payload()

    def snapshot(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        return self.service.dispatch_snapshot(payload).to_payload()

    def poll_events(self, *, since_sequence: int | None = None, limit: int = 100) -> dict[str, Any]:
        events = [item.to_payload() for item in self.service.poll_events(since_sequence=since_sequence, limit=limit)]
        return {
            "ok": True,
            "kind": "event_poll_result",
            "events": events,
            "cursor": self.service.last_event_sequence(),
        }

    def contracts(self) -> dict[str, Any]:
        return {
            "ok": True,
            "kind": "contracts",
            "endpoints": self.service.list_endpoints(),
            "diagnostics": self.service.diagnostics_payload(),
        }

    def event_stream_once(self, *, since_sequence: int | None = None, limit: int = 100) -> str:
        """
        Server-sent-event-like single batch payload for tooling that wants stream framing
        without holding persistent sockets.
        """
        payload = self.poll_events(since_sequence=since_sequence, limit=limit)
        return f"event: integration.events\ndata: {json.dumps(payload, ensure_ascii=True)}\n\n"

    def health(self) -> dict[str, Any]:
        return {
            "ok": True,
            "kind": "health",
            "diagnostics": self.service.diagnostics_payload(),
        }


@dataclass(slots=True)
class LocalHttpIntegrationConfig:
    host: str = "127.0.0.1"
    port: int = 0
    debug: bool = False


class LocalHttpIntegrationAdapter:
    """
    Local-only HTTP adapter for future lightweight clients.

    Routes:
    - POST /v1/command
    - POST /v1/query
    - POST /v1/snapshot
    - GET  /v1/contracts
    - GET  /v1/events?since=<n>&limit=<n>
    - GET  /v1/events/stream?since=<n>&limit=<n> (single SSE frame scaffold)
    - GET  /v1/health
    """

    def __init__(self, service: IntegrationService, config: LocalHttpIntegrationConfig | None = None) -> None:
        self.service = service
        self.config = config or LocalHttpIntegrationConfig()
        self._server: ThreadingHTTPServer | None = None
        self._thread: Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._server is not None and self._thread is not None and self._thread.is_alive()

    @property
    def base_url(self) -> str:
        if self._server is None:
            host = self.config.host
            port = int(self.config.port)
            return f"http://{host}:{port}"
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    def start(self) -> str:
        if self.is_running:
            return self.base_url

        adapter = self

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                if parsed.path == "/v1/health":
                    self._write_json(
                        200,
                        {
                            "ok": True,
                            "kind": "health",
                            "diagnostics": adapter.service.diagnostics_payload(),
                        },
                    )
                    return
                if parsed.path == "/v1/contracts":
                    self._write_json(
                        200,
                        {
                            "ok": True,
                            "kind": "contracts",
                            "endpoints": adapter.service.list_endpoints(),
                            "diagnostics": adapter.service.diagnostics_payload(),
                        },
                    )
                    return
                if parsed.path == "/v1/events":
                    query = parse_qs(parsed.query)
                    since_values = query.get("since", [])
                    limit_values = query.get("limit", [])
                    since = int(since_values[0]) if since_values else None
                    limit = int(limit_values[0]) if limit_values else 100
                    events = [
                        item.to_payload()
                        for item in adapter.service.poll_events(since_sequence=since, limit=limit)
                    ]
                    self._write_json(
                        200,
                        {
                            "ok": True,
                            "kind": "event_poll_result",
                            "events": events,
                            "cursor": adapter.service.last_event_sequence(),
                        },
                    )
                    return
                if parsed.path == "/v1/events/stream":
                    query = parse_qs(parsed.query)
                    since_values = query.get("since", [])
                    limit_values = query.get("limit", [])
                    since = int(since_values[0]) if since_values else None
                    limit = int(limit_values[0]) if limit_values else 100
                    events = [
                        item.to_payload()
                        for item in adapter.service.poll_events(since_sequence=since, limit=limit)
                    ]
                    payload = {
                        "ok": True,
                        "kind": "event_stream_frame",
                        "events": events,
                        "cursor": adapter.service.last_event_sequence(),
                    }
                    self._write_sse("integration.events", payload)
                    return
                self._write_json(
                    404,
                    {
                        "ok": False,
                        "kind": "error",
                        "error": {
                            "code": "route_not_found",
                            "message": f"unsupported route '{parsed.path}'",
                            "status_code": 404,
                        },
                    },
                )

            def do_POST(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                payload = self._read_json()
                if payload is None:
                    self._write_json(
                        400,
                        {
                            "ok": False,
                            "kind": "error",
                            "error": {
                                "code": "invalid_json",
                                "message": "request body must be valid json object",
                                "status_code": 400,
                            },
                        },
                    )
                    return
                if parsed.path == "/v1/command":
                    response = adapter.service.dispatch_command(payload)
                    self._write_response(response)
                    return
                if parsed.path == "/v1/query":
                    response = adapter.service.dispatch_query(payload)
                    self._write_response(response)
                    return
                if parsed.path == "/v1/snapshot":
                    response = adapter.service.dispatch_snapshot(payload)
                    self._write_response(response)
                    return
                self._write_json(
                    404,
                    {
                        "ok": False,
                        "kind": "error",
                        "error": {
                            "code": "route_not_found",
                            "message": f"unsupported route '{parsed.path}'",
                            "status_code": 404,
                        },
                    },
                )

            def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
                if adapter.config.debug:
                    super().log_message(fmt, *args)

            def _read_json(self) -> dict[str, Any] | None:
                try:
                    content_length = int(self.headers.get("Content-Length") or "0")
                except ValueError:
                    content_length = 0
                if content_length <= 0:
                    return {}
                body = self.rfile.read(content_length)
                try:
                    payload = json.loads(body.decode("utf-8"))
                except Exception:  # noqa: BLE001
                    return None
                if not isinstance(payload, dict):
                    return None
                return payload

            def _write_response(self, response: IntegrationResponse) -> None:
                status = 200
                if not response.ok and response.error is not None:
                    status = max(400, int(response.error.status_code))
                self._write_json(status, response.to_payload())

            def _write_json(self, status: int, payload: Mapping[str, Any]) -> None:
                data = _json_bytes(payload)
                self.send_response(int(status))
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _write_sse(self, event_name: str, payload: Mapping[str, Any]) -> None:
                frame = f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=True)}\n\n".encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.send_header("Content-Length", str(len(frame)))
                self.end_headers()
                self.wfile.write(frame)

        self._server = ThreadingHTTPServer((self.config.host, int(self.config.port)), _Handler)
        self._thread = Thread(target=self._server.serve_forever, name="glass-http-integration", daemon=True)
        self._thread.start()
        return self.base_url

    def stop(self) -> None:
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        self._server = None
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

    def __enter__(self) -> LocalHttpIntegrationAdapter:
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.stop()


class WebSocketIntegrationAdapterScaffold:
    """
    Prepared scaffold for future WebSocket transport.

    Intentionally not implemented in this iteration to avoid transport lock-in.
    """

    transport: str = "websocket"
    status: str = "scaffolded"

    def __init__(self, service: IntegrationService) -> None:
        self.service = service

    def start(self) -> None:
        raise RuntimeError("WebSocket adapter is scaffolded only in this iteration.")

    def stop(self) -> None:
        return None


class IpcIntegrationAdapterScaffold:
    """
    Prepared scaffold for future IPC/local process transport.

    Intentionally not implemented in this iteration.
    """

    transport: str = "ipc"
    status: str = "scaffolded"

    def __init__(self, service: IntegrationService) -> None:
        self.service = service

    def start(self) -> None:
        raise RuntimeError("IPC adapter is scaffolded only in this iteration.")

    def stop(self) -> None:
        return None
