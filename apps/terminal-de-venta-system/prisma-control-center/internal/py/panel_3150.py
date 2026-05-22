from __future__ import annotations

import json
import threading
import time
import urllib.request
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from typing import Any

from config_loader import CONTROL_CENTER_PORT, LATEST_ROOT, WEB_ROOT, ensure_log_dirs
from ports_inspector import inspect_port
from process_classifier import classify_owners
from report_writer import export_support_bundle, sanitize_for_public
# PRISMA_BLACKBOX_BRIDGE_V1_PANEL_BEGIN
try:
    from blackbox_bridge import panel_incidents_payload as _prisma_blackbox_panel_incidents_payload
except Exception:
    _prisma_blackbox_panel_incidents_payload = None
# PRISMA_BLACKBOX_BRIDGE_V1_PANEL_END
# PRISMA_BLACKBOX_COMMAND_ITER3_IMPORT_BEGIN
try:
    from blackbox_command_api import blackbox_command_payload as _prisma_blackbox_command_payload
except Exception:
    _prisma_blackbox_command_payload = None
# PRISMA_BLACKBOX_COMMAND_ITER3_IMPORT_END
# PRISMA_CLOUDFLARE_ACTIONS_ITER4_IMPORT_BEGIN
try:
    from ops_command_api import ops_command_payload as _prisma_ops_command_payload
except Exception:
    _prisma_ops_command_payload = None
# PRISMA_CLOUDFLARE_ACTIONS_ITER4_IMPORT_END
# PRISMA_ULTRA_POLISH_RELEASE_ITER5_IMPORT_BEGIN
try:
    from release_status_api import release_status_payload as _prisma_release_status_payload
except Exception:
    _prisma_release_status_payload = None
# PRISMA_ULTRA_POLISH_RELEASE_ITER5_IMPORT_END

# PRISMA_QUALITY_BAY_IMPORT_BEGIN
try:
    from quality_command_api import quality_command_payload as _prisma_quality_command_payload
except Exception:
    _prisma_quality_command_payload = None
# PRISMA_QUALITY_BAY_IMPORT_END

# PRISMA_LICENSE_OPS_IMPORT_BEGIN
try:
    from license_ops_api import license_ops_payload as _prisma_license_ops_payload
except Exception:
    _prisma_license_ops_payload = None
# PRISMA_LICENSE_OPS_IMPORT_END






LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1", "[::1]"}
PUBLIC_HOSTS = {"control.hitechrts.com"}


class PanelHandler(SimpleHTTPRequestHandler):
    server_version = "PRISMAControlCenter/1.0"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib signature.
        return

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
            "connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        )
        super().end_headers()

    def _host_name(self) -> str:
        host = self.headers.get("Host", "")
        return host.split(":", 1)[0].strip().lower()

    def _is_local_request(self) -> bool:
        host = self._host_name()
        client = self.client_address[0] if self.client_address else ""
        return host in LOCAL_HOSTS or client in {"127.0.0.1", "::1"} and host not in PUBLIC_HOSTS

    def _load_health_payload(self, public: bool) -> dict[str, Any]:
        path = LATEST_ROOT / ("public-health.json" if public else "health.json")
        fallback = LATEST_ROOT / "health.json"
        if not path.exists() and public and fallback.exists():
            return sanitize_for_public(json.loads(fallback.read_text(encoding="utf-8")))
        if not path.exists():
            return {
                "empty": True,
                "overallStatus": "EMPTY",
                "healthScore": 0,
                "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL",
                "recommendedNextAction": "Corre health para generar el primer reporte.",
                "services": [],
                "cloudflare": {"status": "EMPTY", "publicEndpoints": []},
                "control_center": {
                    "public_url": "https://control.hitechrts.com/",
                    "public_mode": "PUBLIC_REDACTED",
                    "status": "EMPTY",
                    "health_score": 0,
                    "last_updated": "",
                    "services_summary": [],
                    "cloudflare_summary": [],
                    "recommendations": ["Corre health para generar el primer reporte."],
                },
            }
        payload = json.loads(path.read_text(encoding="utf-8"))
        return sanitize_for_public(payload) if public and path.name != "public-health.json" else payload

    def _send_json(self, payload: Any, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=True, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler name.
        if self.path in {"/api/health", "/api/health/"}:
            try:
                self._send_json(self._load_health_payload(public=not self._is_local_request()))
            except Exception as exc:  # noqa: BLE001 - panel must degrade gracefully.
                self._send_json({"empty": True, "overallStatus": "ERROR", "error": str(exc)}, status=500)
            return
        if self.path in {"/api/public-health", "/api/public-health/"}:
            try:
                self._send_json(self._load_health_payload(public=True))
            except Exception as exc:  # noqa: BLE001 - panel must degrade gracefully.
                self._send_json({"empty": True, "overallStatus": "ERROR", "safetyMode": "PUBLIC_REDACTED", "error": str(exc)}, status=500)
            return
        # PRISMA_BLACKBOX_BRIDGE_V1_PANEL_BEGIN
        # PRISMA_BLACKBOX_COMMAND_ITER3_ROUTE_BEGIN
        # PRISMA_CLOUDFLARE_ACTIONS_ITER4_ROUTE_BEGIN
        # PRISMA_ULTRA_POLISH_RELEASE_ITER5_ROUTE_BEGIN

        # PRISMA_LICENSE_OPS_ROUTE_BEGIN
        if self.path.startswith("/api/license-ops"):
            try:
                if _prisma_license_ops_payload is None:
                    self._send_json({"ok": False, "status": "LICENSE_OPS_UNAVAILABLE"}, status=503)
                else:
                    self._send_json(_prisma_license_ops_payload(self.path, public=not self._is_local_request()))
            except Exception as exc:
                self._send_json({"ok": False, "status": "LICENSE_OPS_ERROR", "error": str(exc)}, status=500)
            return
        # PRISMA_LICENSE_OPS_ROUTE_END

        # PRISMA_QUALITY_BAY_ROUTE_BEGIN
        if self.path.startswith("/api/quality"):
            try:
                if _prisma_quality_command_payload is None:
                    self._send_json({"ok": False, "status": "QUALITY_COMMAND_UNAVAILABLE"}, status=503)
                else:
                    self._send_json(_prisma_quality_command_payload(self.path, public=not self._is_local_request()))
            except Exception as exc:
                self._send_json({"ok": False, "status": "QUALITY_COMMAND_ERROR", "error": str(exc)}, status=500)
            return
        # PRISMA_QUALITY_BAY_ROUTE_END
        if self.path.startswith("/api/release"):
            try:
                if _prisma_release_status_payload is None:
                    self._send_json({"ok": False, "status": "RELEASE_STATUS_UNAVAILABLE"}, status=503)
                else:
                    self._send_json(_prisma_release_status_payload(self.path, public=not self._is_local_request()))
            except Exception as exc:
                self._send_json({"ok": False, "status": "RELEASE_STATUS_ERROR", "error": str(exc)}, status=500)
            return
        # PRISMA_ULTRA_POLISH_RELEASE_ITER5_ROUTE_END
        if self.path.startswith("/api/ops"):
            try:
                if _prisma_ops_command_payload is None:
                    self._send_json({"ok": False, "status": "OPS_COMMAND_UNAVAILABLE"}, status=503)
                else:
                    self._send_json(_prisma_ops_command_payload(self.path, public=not self._is_local_request()))
            except Exception as exc:
                self._send_json({"ok": False, "status": "OPS_COMMAND_ERROR", "error": str(exc)}, status=500)
            return
        # PRISMA_CLOUDFLARE_ACTIONS_ITER4_ROUTE_END
        if self.path.startswith("/api/blackbox"):
            try:
                if _prisma_blackbox_command_payload is None:
                    self._send_json({"ok": False, "status": "BLACKBOX_COMMAND_UNAVAILABLE"}, status=503)
                else:
                    self._send_json(_prisma_blackbox_command_payload(self.path, public=not self._is_local_request()))
            except Exception as exc:
                self._send_json({"ok": False, "status": "BLACKBOX_COMMAND_ERROR", "error": str(exc)}, status=500)
            return
        # PRISMA_BLACKBOX_COMMAND_ITER3_ROUTE_END
        if self.path in {"/api/incidents", "/api/incidents/"}:
            try:
                if _prisma_blackbox_panel_incidents_payload is None:
                    self._send_json(
                        {"ok": False, "status": "BRIDGE_UNAVAILABLE", "activeIncidents": []},
                        status=503,
                    )
                else:
                    self._send_json(
                        _prisma_blackbox_panel_incidents_payload(
                            public=not self._is_local_request()
                        )
                    )
            except Exception as exc:
                self._send_json(
                    {"ok": False, "status": "ERROR", "error": str(exc), "activeIncidents": []},
                    status=500,
                )
            return
        # PRISMA_BLACKBOX_BRIDGE_V1_PANEL_END
        if self.path in {"/api/export-support-bundle", "/api/export-support-bundle/"}:
            if not self._is_local_request():
                self._send_json(
                    {
                        "ok": False,
                        "status": "PUBLIC_REDACTED_READ_ONLY",
                        "message": "Support bundle export is disabled in public read-only mode.",
                    },
                    status=403,
                )
                return
            self._send_json(export_support_bundle())
            return
        if self.path in {"/latest/health.html", "/latest/health.html/"}:
            latest_html = LATEST_ROOT / "health.html"
            if latest_html.exists():
                data = latest_html.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            self.send_error(404, "No latest report")
            return
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()


def panel_port_status() -> dict[str, Any]:
    port_report = inspect_port(CONTROL_CENTER_PORT)
    owners = classify_owners(port_report, action="panel", service_id="panel-3150")
    return {"port": CONTROL_CENTER_PORT, "portReport": port_report, "owners": owners}


def run_panel(open_browser: bool = False) -> int:
    ensure_log_dirs()
    status = panel_port_status()
    owners = status["owners"]
    if owners:
        unknown = [owner for owner in owners if not owner.get("classification", {}).get("recognized")]
        if unknown:
            print(json.dumps({"status": "BLOCKED_UNKNOWN_PROCESS", "port": CONTROL_CENTER_PORT, "owners": unknown}, indent=2))
            return 3
        if open_browser:
            webbrowser.open(f"http://127.0.0.1:{CONTROL_CENTER_PORT}/")
        print(f"Panel already appears to be running on http://127.0.0.1:{CONTROL_CENTER_PORT}/")
        return 0

    httpd = ThreadingHTTPServer(("127.0.0.1", CONTROL_CENTER_PORT), PanelHandler)
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(f"http://127.0.0.1:{CONTROL_CENTER_PORT}/")).start()
    print(f"PRISMA Control Center panel: http://127.0.0.1:{CONTROL_CENTER_PORT}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


def smoke_panel() -> dict[str, Any]:
    ensure_log_dirs()
    status = panel_port_status()
    if status["owners"]:
        unknown = [owner for owner in status["owners"] if not owner.get("classification", {}).get("recognized")]
        if unknown:
            return {"ok": False, "status": "BLOCKED_UNKNOWN_PROCESS", "owners": unknown}
    server = ThreadingHTTPServer(("127.0.0.1", CONTROL_CENTER_PORT), PanelHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.4)
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{CONTROL_CENTER_PORT}/", timeout=5) as response:
            html = response.read(200000).decode("utf-8", errors="ignore")
        with urllib.request.urlopen(f"http://127.0.0.1:{CONTROL_CENTER_PORT}/api/health", timeout=5) as response:
            health = json.loads(response.read(200000).decode("utf-8", errors="ignore"))
        public_request = urllib.request.Request(
            f"http://127.0.0.1:{CONTROL_CENTER_PORT}/api/health",
            headers={"Host": "control.hitechrts.com"},
        )
        with urllib.request.urlopen(public_request, timeout=5) as response:
            public_health = json.loads(response.read(200000).decode("utf-8", errors="ignore"))
            public_text = json.dumps(public_health, ensure_ascii=False)
        sensitive_hits = [
            needle
            for needle in ["commandLine", "executablePath", "C:\\Users\\", "F:\\repos\\hitech-os\\", "credentials-file", "token", "secret"]
            if needle.lower() in public_text.lower()
        ]
        return {
            "ok": response.status == 200 and "PRISMA Control Center" in html and public_health.get("safetyMode") == "PUBLIC_REDACTED" and not sensitive_hits,
            "status": "PASS",
            "htmlBytes": len(html),
            "healthStatus": health.get("overallStatus"),
            "publicMode": public_health.get("safetyMode"),
            "publicSensitiveHits": sensitive_hits,
        }
    except Exception as exc:  # noqa: BLE001 - smoke returns diagnostics.
        return {"ok": False, "status": "FAIL", "error": str(exc)}
    finally:
        server.shutdown()
        server.server_close()
