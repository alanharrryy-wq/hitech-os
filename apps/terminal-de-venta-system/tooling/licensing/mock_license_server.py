from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

FIXTURE_MAP = {
    "tablet-solo": "tooling/licensing/fixtures/tablet-solo.active.signed.license.json",
    "tablet-pro": "tooling/licensing/fixtures/tablet-pro.active.signed.license.json",
    "tablet-pc-required": "tooling/licensing/fixtures/tablet-pc-required.active.signed.license.json",
    "expired": "tooling/productization/examples/licenses/expired.signed.license.json",
    "suspended": "tooling/productization/examples/licenses/suspended.signed.license.json",
    "revoked": "tooling/productization/examples/licenses/revoked.signed.license.json",
    "tampered": "tooling/licensing/fixtures/tampered.signed.license.json",
}


def make_handler(root: Path):
    class Handler(BaseHTTPRequestHandler):
        server_version = "PRISMALicenseMock/0.4"

        def _send_json(self, code: int, payload: dict):
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/health":
                self._send_json(200, {"ok": True, "service": "prisma-license-mock"})
                return
            if parsed.path == "/licenses/current":
                qs = parse_qs(parsed.query)
                fixture_key = (qs.get("fixture") or ["tablet-pc-required"])[0]
                rel = FIXTURE_MAP.get(fixture_key)
                if not rel:
                    self._send_json(404, {"ok": False, "code": "UNKNOWN_FIXTURE", "available": sorted(FIXTURE_MAP)})
                    return
                path = root / rel
                if not path.exists():
                    self._send_json(404, {"ok": False, "code": "FIXTURE_NOT_FOUND", "path": str(path)})
                    return
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except Exception as exc:
                    self._send_json(500, {"ok": False, "code": "FIXTURE_READ_FAILED", "error": str(exc)})
                    return
                self._send_json(200, {"ok": True, "data": data, "fixture": fixture_key})
                return
            self._send_json(404, {"ok": False, "code": "NOT_FOUND", "path": parsed.path})

        def log_message(self, fmt, *args):
            print("[mock-license] " + fmt % args)

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description="PRISMA local mock license server")
    parser.add_argument("--root", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4117)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")
    server = ThreadingHTTPServer((args.host, args.port), make_handler(root))
    print(f"PRISMA mock license server listening at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping mock license server")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
