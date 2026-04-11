from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Tuple

from .engine import build_error_payload, build_health_report, get_capabilities, parse_request, run_job
from .models import ModelValidationError


def _json_response(status_code: int, payload: Any) -> Tuple[int, bytes]:
    content = json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2)
    return status_code, f"{content}\n".encode("utf-8")


class AgentHttpHandler(BaseHTTPRequestHandler):
    server_version = "HitechAgent/0.2.0"

    def _send(self, status_code: int, payload: Any) -> None:
        code, body = _json_response(status_code, payload)
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Any:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        text = raw.decode("utf-8").strip() or "{}"
        return json.loads(text)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/capabilities":
            self._send(200, get_capabilities().model_dump())
            return

        if self.path == "/health":
            self._send(200, build_health_report().model_dump())
            return

        self._send(
            404,
            {
                "error": "NOT_FOUND",
                "path": self.path,
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/jobs/run":
            self._send(
                404,
                {
                    "error": "NOT_FOUND",
                    "path": self.path,
                },
            )
            return

        try:
            body = self._read_json()
        except json.JSONDecodeError:
            self._send(400, build_error_payload("INVALID_JSON", "Request body must be valid JSON"))
            return

        try:
            request = parse_request(body)
        except (ModelValidationError, ValueError) as exc:
            self._send(400, build_error_payload("INVALID_JOB_REQUEST", str(exc)))
            return

        result = run_job(request)
        self._send(200, result.model_dump())

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def run_server(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), AgentHttpHandler)
    try:
        print(f"ai-agent listening on http://{host}:{port}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HITECH deterministic ai-agent")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8001, type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
