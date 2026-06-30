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
# PRISMA_DATA_LIFECYCLE_IMPORT_BEGIN
try:
    from lifecycle_api import lifecycle_payload as _prisma_lifecycle_payload
except Exception:
    _prisma_lifecycle_payload = None
# PRISMA_DATA_LIFECYCLE_IMPORT_END
# PRISMA_LIFEBOOM2_FAST_HEALTH_IMPORT_BEGIN
try:
    from lifecycle_fast_health import lifecycle_fast_health_payload as _prisma_lifecycle_fast_health_payload
except Exception:
    _prisma_lifecycle_fast_health_payload = None
# PRISMA_LIFEBOOM2_FAST_HEALTH_IMPORT_END
# PRISMO_AI_BRIDGE_IMPORT_BEGIN
try:
    from prismo_ai_bridge import (
        prismo_demo_payload as _prismo_demo_payload,
        prismo_query_payload as _prismo_query_payload,
        prismo_status_payload as _prismo_status_payload,
        prismo_theater_query_payload as _prismo_theater_query_payload,
        prismo_tools_status_payload as _prismo_tools_status_payload,
    )
except Exception:
    _prismo_demo_payload = None
    _prismo_query_payload = None
    _prismo_status_payload = None
    _prismo_theater_query_payload = None
    _prismo_tools_status_payload = None
# PRISMO_AI_BRIDGE_IMPORT_END
# PRISMO_APP_LIVE_CONTEXT_IMPORT_BEGIN
try:
    from prismo_app_live_context import app_live_context_payload as _prismo_app_live_context_payload
except Exception:
    _prismo_app_live_context_payload = None
# PRISMO_APP_LIVE_CONTEXT_IMPORT_END
# PRISMO_LEARNING_CORE_V1_IMPORT_BEGIN
try:
    from prismo_learning.api import (
        learning_status_payload as _prismo_learning_status_payload,
        learning_evidence_index_payload as _prismo_learning_evidence_index_payload,
        learning_recommend_protocol_payload as _prismo_learning_recommend_protocol_payload,
        learning_insights_payload as _prismo_learning_insights_payload,
        learning_graph_payload as _prismo_learning_graph_payload,
        learning_feedback_payload as _prismo_learning_feedback_payload,
        learning_intake_status_payload as _prismo_learning_intake_status_payload,
        learning_intake_plan_payload as _prismo_learning_intake_plan_payload,
        learning_intake_run_payload as _prismo_learning_intake_run_payload,
        learning_patterns_payload as _prismo_learning_patterns_payload,
        learning_authority_payload as _prismo_learning_authority_payload,
        learning_f3_status_payload as _prismo_learning_f3_status_payload,
        learning_f3_run_payload as _prismo_learning_f3_run_payload,
        learning_safe_summary_payload as _prismo_learning_safe_summary_payload,
        learning_technical_drawer_payload as _prismo_learning_technical_drawer_payload,
        learning_feedback_stats_payload as _prismo_learning_feedback_stats_payload,
        learning_compaction_status_payload as _prismo_learning_compaction_status_payload,
        learning_compaction_run_payload as _prismo_learning_compaction_run_payload,
        learning_governance_status_payload as _prismo_learning_governance_status_payload,
        learning_context_enrichment_payload as _prismo_learning_context_enrichment_payload,
        learning_action_status_payload as _prismo_learning_action_status_payload,
        learning_action_preview_payload as _prismo_learning_action_preview_payload,
        learning_completion_status_payload as _prismo_learning_completion_status_payload,
        learning_completion_run_payload as _prismo_learning_completion_run_payload,
    )
except Exception:
    _prismo_learning_status_payload = None
    _prismo_learning_evidence_index_payload = None
    _prismo_learning_recommend_protocol_payload = None
    _prismo_learning_insights_payload = None
    _prismo_learning_graph_payload = None
    _prismo_learning_feedback_payload = None
    _prismo_learning_intake_status_payload = None
    _prismo_learning_intake_plan_payload = None
    _prismo_learning_intake_run_payload = None
    _prismo_learning_patterns_payload = None
    _prismo_learning_authority_payload = None
    _prismo_learning_f3_status_payload = None
    _prismo_learning_f3_run_payload = None
    _prismo_learning_safe_summary_payload = None
    _prismo_learning_technical_drawer_payload = None
    _prismo_learning_feedback_stats_payload = None
    _prismo_learning_compaction_status_payload = None
    _prismo_learning_compaction_run_payload = None
    _prismo_learning_governance_status_payload = None
    _prismo_learning_context_enrichment_payload = None
    _prismo_learning_action_status_payload = None
    _prismo_learning_action_preview_payload = None
    _prismo_learning_completion_status_payload = None
    _prismo_learning_completion_run_payload = None
# PRISMO_LEARNING_CORE_V1_IMPORT_END








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
        # PRISMA_MOTORES_FIX2_LOCAL_API_CORS_BEGIN
        origin = self.headers.get("Origin", "")
        if origin.startswith(("http://127.0.0.1:", "http://localhost:", "http://[::1]:")):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        # PRISMA_MOTORES_FIX2_LOCAL_API_CORS_END
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
            "connect-src 'self' http://127.0.0.1:3150 http://localhost:3150 ws://127.0.0.1:3150 ws://localhost:3150; font-src 'self'; frame-src 'self' about:; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        )
        super().end_headers()

    def _host_name(self) -> str:
        host = self.headers.get("Host", "")
        return host.split(":", 1)[0].strip().lower()

    def _is_local_request(self) -> bool:
        host = self._host_name()
        client = self.client_address[0] if self.client_address else ""
        return host in LOCAL_HOSTS or client in {"127.0.0.1", "::1"} and host not in PUBLIC_HOSTS

    # PRISMA_MOTORES_FIX2_OPTIONS_BEGIN
    def do_OPTIONS(self) -> None:
        if self.path.startswith("/api/"):
            self.send_response(204)
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()
    # PRISMA_MOTORES_FIX2_OPTIONS_END

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
        # PRISMO_QUERY_NULL_GUARD_PANEL_SEND_JSON
        if payload is None:
            payload = {
                "ok": False,
                "status": "error",
                "request_id": "prismo_panel_null_guard",
                "mode": "ASK",
                "demo_mode": False,
                "read_only": True,
                "mutation_allowed": False,
                "direct_answer": "PRISMO evitó una respuesta null del endpoint y devolvió un error seguro estructurado.",
                "certainty_level": "NO_CONFIRMADO",
                "authority": {
                    "winning_source": "panel_3150.py",
                    "winning_source_type": "code",
                    "precedence_applied": ["runtime_guard", "read_only_v1"],
                    "notes": "El handler detectó payload None antes de serializar JSON."
                },
                "evidence": [],
                "risk": {
                    "level": "medium",
                    "summary": "El bridge interno devolvió None.",
                    "reasons": ["Respuesta no serializable o vacía en /api/prismo/query."],
                    "mitigations": ["Revisar ledger PRISMO y provider Gemini."]
                },
                "safe_next_step": "Reintentar la consulta o revisar logs sanitizados del bridge.",
                "render_blocks": [],
                "warnings": ["PRISMO_QUERY_NULL_GUARD_PANEL_SEND_JSON"],
                "errors": [
                    {
                        "code": "PRISMO_QUERY_RETURNED_NULL",
                        "message": "PRISMO query returned None before JSON serialization.",
                        "safe_message": "El endpoint devolvió error seguro en vez de null.",
                        "recoverable": True
                    }
                ],
                "meta": {
                    "provider": "gemini",
                    "schema_version": "1.0.0",
                    "generated_at": "",
                    "input_chars": 0,
                    "render_block_count": 0
                }
            }
            if status == 200:
                status = 500
        data = json.dumps(payload, ensure_ascii=True, indent=2).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return

    def _read_json_body(self, max_bytes: int = 750000) -> dict[str, Any]:
        length_raw = self.headers.get("Content-Length", "0")
        try:
            length = int(length_raw)
        except ValueError:
            raise ValueError("Invalid Content-Length")
        if length < 0 or length > max_bytes:
            raise ValueError("Request body exceeds PRISMO safe size limit")
        raw = self.rfile.read(length) if length else b"{}"
        if not raw:
            return {}
        try:
            payload = json.loads(raw.decode("utf-8", errors="replace"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON body: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler name.
        if self.path in {"/api/prismo/theater/query", "/api/prismo/theater/query/"}:
            if not self._is_local_request():
                self._send_json(
                    {
                        "ok": False,
                        "status": "blocked",
                        "blocked": True,
                        "block_reason": "PUBLIC_REDACTED_READ_ONLY",
                        "direct_answer": "Bloqueado: PRISMO Theater Query sólo acepta consultas locales para proteger evidencia interna.",
                    },
                    status=403,
                )
                return
            try:
                if _prismo_theater_query_payload is None:
                    self._send_json({"ok": False, "status": "error", "error": "PRISMO Theater adapter unavailable"}, status=503)
                    return
                payload = self._read_json_body(max_bytes=750000)
                self._send_json(_prismo_theater_query_payload(payload, public=False))
            except ValueError as exc:
                self._send_json(
                    {
                        "ok": False,
                        "status": "blocked",
                        "blocked": True,
                        "block_reason": "BLOCKED_SIZE_OR_JSON_LIMIT",
                        "direct_answer": "Bloqueado: la solicitud no cumplió el límite seguro de JSON de PRISMO Theater.",
                        "safe_next_step": "Reduce la evidencia temporal y vuelve a intentar.",
                        "error": str(exc),
                    },
                    status=413,
                )
            except Exception as exc:  # noqa: BLE001 - never expose stack traces to UI.
                self._send_json(
                    {
                        "ok": False,
                        "status": "error",
                        "direct_answer": "No se pudo validar Theater Query. No se ejecutó ninguna acción.",
                        "error": str(exc),
                    },
                    status=500,
                )
            return

        if self.path in {"/api/prismo/query", "/api/prismo/query/"}:
            if not self._is_local_request():
                self._send_json(
                    {
                        "ok": False,
                        "status": "blocked",
                        "blocked": True,
                        "block_reason": "PUBLIC_REDACTED_READ_ONLY",
                        "direct_answer": "Bloqueado: PRISMO query v1 solo acepta consultas locales para proteger evidencia interna.",
                    },
                    status=403,
                )
                return
            try:
                if _prismo_query_payload is None:
                    self._send_json({"ok": False, "status": "error", "error": "PRISMO bridge unavailable"}, status=503)
                    return
                payload = self._read_json_body(max_bytes=750000)
                result = _prismo_query_payload(payload, public=False)
                if not isinstance(result, dict):
                    result = {
                        "ok": False,
                        "status": "error",
                        "request_id": "prismo_panel_query_type_guard",
                        "mode": str(payload.get("mode") or "ASK").upper() if isinstance(payload, dict) else "ASK",
                        "demo_mode": False,
                        "read_only": True,
                        "mutation_allowed": False,
                        "direct_answer": "PRISMO evitó devolver una respuesta vacía o no-objeto desde /api/prismo/query.",
                        "certainty_level": "NO_CONFIRMADO",
                        "authority": {
                            "winning_source": "panel_3150.py",
                            "winning_source_type": "code",
                            "precedence_applied": ["runtime_guard", "read_only_v1"],
                            "notes": "El handler convirtió una respuesta inválida del bridge en JSON seguro."
                        },
                        "evidence": [],
                        "risk": {
                            "level": "medium",
                            "summary": "El bridge devolvió un tipo inválido.",
                            "reasons": [f"Tipo recibido: {type(result).__name__}"],
                            "mitigations": ["Corregir provider o bridge; no se ejecutó ninguna acción."]
                        },
                        "safe_next_step": "Reintentar y revisar reporte PRISMO.",
                        "render_blocks": [],
                        "warnings": ["PRISMO_QUERY_NULL_GUARD_PANEL_POST"],
                        "errors": [
                            {
                                "code": "PRISMO_QUERY_RETURNED_NON_OBJECT",
                                "message": f"Expected dict response, got {type(result).__name__}",
                                "safe_message": "El endpoint devolvió error seguro estructurado.",
                                "recoverable": True
                            }
                        ],
                        "meta": {
                            "provider": "gemini",
                            "schema_version": "1.0.0",
                            "generated_at": "",
                            "input_chars": len(json.dumps(payload, ensure_ascii=True)) if isinstance(payload, dict) else 0,
                            "render_block_count": 0
                        }
                    }
                self._send_json(result)
            except ValueError as exc:
                self._send_json(
                    {
                        "ok": False,
                        "status": "blocked",
                        "blocked": True,
                        "block_reason": "BLOCKED_SIZE_OR_JSON_LIMIT",
                        "direct_answer": "Bloqueado: la solicitud no cumplió el límite seguro de JSON de PRISMO.",
                        "safe_next_step": "Reduce la evidencia temporal y vuelve a intentar.",
                        "error": str(exc),
                    },
                    status=413,
                )
            except Exception as exc:  # noqa: BLE001 - never expose stack traces to UI.
                self._send_json(
                    {
                        "ok": False,
                        "status": "error",
                        "direct_answer": "No se pudo validar la consulta de PRISMO. No se ejecutó ninguna acción.",
                        "error": str(exc),
                    },
                    status=500,
                )
            return






        # PRISMO_LEARNING_CORE_V1_POST_ROUTE_BEGIN
        if self.path in {"/api/prismo/learning/completion/run", "/api/prismo/learning/completion/run/"}:
            if not self._is_local_request(): self._send_json({"ok":False,"status":"blocked","block_reason":"PUBLIC_COMPLETION_RUN_BLOCKED","read_only":True,"mutation_allowed":False}, status=403); return
            self._send_json(_prismo_learning_completion_run_payload(public=False) if _prismo_learning_completion_run_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_completion_run_payload else 503); return
        if self.path in {"/api/prismo/learning/memory/compact/run", "/api/prismo/learning/memory/compact/run/"}:
            if not self._is_local_request(): self._send_json({"ok":False,"status":"blocked","block_reason":"PUBLIC_COMPACTION_RUN_BLOCKED","read_only":True,"mutation_allowed":False}, status=403); return
            self._send_json(_prismo_learning_compaction_run_payload(public=False) if _prismo_learning_compaction_run_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_compaction_run_payload else 503); return
        if self.path in {"/api/prismo/learning/actions/preview", "/api/prismo/learning/actions/preview/"}:
            payload = self._read_json_body(max_bytes=250000) if self._is_local_request() else {}
            self._send_json(_prismo_learning_action_preview_payload(payload, public=not self._is_local_request()) if _prismo_learning_action_preview_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_action_preview_payload else 503); return
        if self.path in {"/api/prismo/learning/f3/run", "/api/prismo/learning/f3/run/"}:
            if not self._is_local_request(): self._send_json({"ok":False,"status":"blocked","block_reason":"PUBLIC_F3_RUN_BLOCKED","read_only":True,"mutation_allowed":False}, status=403); return
            self._send_json(_prismo_learning_f3_run_payload(public=False) if _prismo_learning_f3_run_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_f3_run_payload else 503); return
        if self.path in {"/api/prismo/learning/feedback", "/api/prismo/learning/feedback/"}:
            if not self._is_local_request(): self._send_json({"ok":False,"status":"blocked","block_reason":"PUBLIC_FEEDBACK_BLOCKED","read_only":True,"mutation_allowed":False}, status=403); return
            payload = self._read_json_body(max_bytes=250000)
            self._send_json(_prismo_learning_feedback_payload(payload, public=False) if _prismo_learning_feedback_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_feedback_payload else 503); return
        if self.path in {"/api/prismo/learning/intake/run", "/api/prismo/learning/intake/run/"}:
            if not self._is_local_request(): self._send_json({"ok":False,"status":"blocked","block_reason":"PUBLIC_INTAKE_RUN_BLOCKED","read_only":True,"mutation_allowed":False}, status=403); return
            self._send_json(_prismo_learning_intake_run_payload(public=False) if _prismo_learning_intake_run_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_intake_run_payload else 503); return
        # PRISMO_LEARNING_CORE_V1_POST_ROUTE_END

        self.send_error(404, "Unknown POST endpoint")

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
        # PRISMO_AI_BRIDGE_ROUTE_BEGIN
        if self.path in {"/api/prismo/status", "/api/prismo/status/"}:
            try:
                if _prismo_status_payload is None:
                    self._send_json({"ok": False, "status": "PRISMO_UNAVAILABLE"}, status=503)
                else:
                    self._send_json(_prismo_status_payload(public=not self._is_local_request()))
            except Exception as exc:  # noqa: BLE001 - status must degrade gracefully.
                self._send_json({"ok": False, "status": "PRISMO_STATUS_ERROR", "error": str(exc)}, status=500)
            return
        if self.path in {"/api/prismo/demo-response", "/api/prismo/demo-response/"}:
            try:
                if _prismo_demo_payload is None:
                    self._send_json({"ok": False, "status": "PRISMO_UNAVAILABLE"}, status=503)
                else:
                    self._send_json(_prismo_demo_payload())
            except Exception as exc:  # noqa: BLE001 - demo must degrade gracefully.
                self._send_json({"ok": False, "status": "PRISMO_DEMO_ERROR", "error": str(exc)}, status=500)
            return
        if self.path in {"/api/prismo/tools/status", "/api/prismo/tools/status/"}:
            try:
                if _prismo_tools_status_payload is None:
                    self._send_json({"ok": False, "status": "PRISMO_UNAVAILABLE"}, status=503)
                else:
                    self._send_json(_prismo_tools_status_payload(public=not self._is_local_request()))
            except Exception as exc:  # noqa: BLE001 - tools status must degrade gracefully.
                self._send_json({"ok": False, "status": "PRISMO_TOOLS_STATUS_ERROR", "error": str(exc)}, status=500)
            return







        if self.path.startswith("/api/prismo/app-live-context") or self.path.startswith("/api/prismo/project-brain"):
            if not self._is_local_request():
                self._send_json({"ok": False, "status": "blocked", "block_reason": "PUBLIC_APP_LIVE_CONTEXT_BLOCKED", "read_only": True, "mutation_allowed": False}, status=403)
                return
            raw_query = ""
            if "?" in self.path:
                from urllib.parse import parse_qs, urlparse
                raw_query = (parse_qs(urlparse(self.path).query).get("q") or [""])[0]
            try:
                self._send_json(_prismo_app_live_context_payload(query=raw_query, public=False) if _prismo_app_live_context_payload else {"ok": False, "status": "PRISMO_APP_LIVE_CONTEXT_UNAVAILABLE", "read_only": True, "mutation_allowed": False}, status=200 if _prismo_app_live_context_payload else 503)
            except Exception as exc:
                self._send_json({"ok": False, "status": "PRISMO_APP_LIVE_CONTEXT_ERROR", "error": str(exc), "read_only": True, "mutation_allowed": False}, status=500)
            return

        # PRISMO_LEARNING_CORE_V1_ROUTE_BEGIN
        if self.path in {"/api/prismo/learning/status", "/api/prismo/learning/status/"}:
            self._send_json(_prismo_learning_status_payload(public=not self._is_local_request()) if _prismo_learning_status_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_status_payload else 503); return
        if self.path in {"/api/prismo/learning/evidence-index", "/api/prismo/learning/evidence-index/"}:
            self._send_json(_prismo_learning_evidence_index_payload(public=not self._is_local_request()) if _prismo_learning_evidence_index_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_evidence_index_payload else 503); return
        if self.path.startswith("/api/prismo/learning/recommend-protocol"):
            raw_query = ""
            if "?" in self.path:
                from urllib.parse import parse_qs, urlparse
                raw_query = (parse_qs(urlparse(self.path).query).get("q") or [""])[0]
            self._send_json(_prismo_learning_recommend_protocol_payload(query=raw_query, public=not self._is_local_request()) if _prismo_learning_recommend_protocol_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_recommend_protocol_payload else 503); return
        if self.path in {"/api/prismo/learning/insights", "/api/prismo/learning/insights/"}:
            self._send_json(_prismo_learning_insights_payload(public=not self._is_local_request()) if _prismo_learning_insights_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_insights_payload else 503); return
        if self.path in {"/api/prismo/learning/graph", "/api/prismo/learning/graph/"}:
            self._send_json(_prismo_learning_graph_payload(public=not self._is_local_request()) if _prismo_learning_graph_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_graph_payload else 503); return
        if self.path in {"/api/prismo/learning/patterns", "/api/prismo/learning/patterns/"}:
            self._send_json(_prismo_learning_patterns_payload(public=not self._is_local_request()) if _prismo_learning_patterns_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_patterns_payload else 503); return
        if self.path in {"/api/prismo/learning/authority", "/api/prismo/learning/authority/"}:
            self._send_json(_prismo_learning_authority_payload(public=not self._is_local_request()) if _prismo_learning_authority_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_authority_payload else 503); return
        if self.path in {"/api/prismo/learning/f3/status", "/api/prismo/learning/f3/status/"}:
            self._send_json(_prismo_learning_f3_status_payload(public=not self._is_local_request()) if _prismo_learning_f3_status_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_f3_status_payload else 503); return
        if self.path in {"/api/prismo/learning/intake/status", "/api/prismo/learning/intake/status/"}:
            self._send_json(_prismo_learning_intake_status_payload(public=not self._is_local_request()) if _prismo_learning_intake_status_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_intake_status_payload else 503); return
        if self.path in {"/api/prismo/learning/safe-summary", "/api/prismo/learning/safe-summary/"}:
            self._send_json(_prismo_learning_safe_summary_payload(public=not self._is_local_request()) if _prismo_learning_safe_summary_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_safe_summary_payload else 503); return
        if self.path in {"/api/prismo/learning/technical-drawer", "/api/prismo/learning/technical-drawer/"}:
            if not self._is_local_request(): self._send_json({"ok":False,"status":"blocked","block_reason":"PUBLIC_TECHNICAL_DRAWER_BLOCKED","read_only":True,"mutation_allowed":False}, status=403); return
            self._send_json(_prismo_learning_technical_drawer_payload(public=False) if _prismo_learning_technical_drawer_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_technical_drawer_payload else 503); return
        if self.path in {"/api/prismo/learning/feedback/stats", "/api/prismo/learning/feedback/stats/"}:
            self._send_json(_prismo_learning_feedback_stats_payload(public=not self._is_local_request()) if _prismo_learning_feedback_stats_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_feedback_stats_payload else 503); return
        if self.path in {"/api/prismo/learning/memory/compact/status", "/api/prismo/learning/memory/compact/status/"}:
            self._send_json(_prismo_learning_compaction_status_payload(public=not self._is_local_request()) if _prismo_learning_compaction_status_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_compaction_status_payload else 503); return
        if self.path in {"/api/prismo/learning/governance/status", "/api/prismo/learning/governance/status/"}:
            self._send_json(_prismo_learning_governance_status_payload(public=not self._is_local_request()) if _prismo_learning_governance_status_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_governance_status_payload else 503); return
        if self.path.startswith("/api/prismo/learning/context/enrich"):
            raw_query = ""
            if "?" in self.path:
                from urllib.parse import parse_qs, urlparse
                raw_query = (parse_qs(urlparse(self.path).query).get("q") or [""])[0]
            self._send_json(_prismo_learning_context_enrichment_payload(query=raw_query, public=not self._is_local_request()) if _prismo_learning_context_enrichment_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_context_enrichment_payload else 503); return
        if self.path in {"/api/prismo/learning/actions/status", "/api/prismo/learning/actions/status/"}:
            self._send_json(_prismo_learning_action_status_payload(public=not self._is_local_request()) if _prismo_learning_action_status_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_action_status_payload else 503); return
        if self.path in {"/api/prismo/learning/completion/status", "/api/prismo/learning/completion/status/"}:
            self._send_json(_prismo_learning_completion_status_payload(public=not self._is_local_request()) if _prismo_learning_completion_status_payload else {"ok":False,"status":"PRISMO_LEARNING_UNAVAILABLE","read_only":True,"mutation_allowed":False}, status=200 if _prismo_learning_completion_status_payload else 503); return
        # PRISMO_LEARNING_CORE_V1_ROUTE_END

        # PRISMO_AI_BRIDGE_ROUTE_END
        # PRISMA_BLACKBOX_BRIDGE_V1_PANEL_BEGIN
        # PRISMA_BLACKBOX_COMMAND_ITER3_ROUTE_BEGIN
        # PRISMA_CLOUDFLARE_ACTIONS_ITER4_ROUTE_BEGIN
        # PRISMA_ULTRA_POLISH_RELEASE_ITER5_ROUTE_BEGIN


        # PRISMA_LIFEBOOM2_FAST_HEALTH_ROUTE_BEGIN
        _prisma_lifeboom2_path = self.path.split("?", 1)[0]
        if _prisma_lifeboom2_path in {"/api/lifecycle/health", "/api/lifecycle/health/"}:
            try:
                if _prisma_lifecycle_fast_health_payload is None:
                    self._send_json({"ok": False, "status": "LIFECYCLE_FAST_HEALTH_UNAVAILABLE"}, status=503)
                else:
                    self._send_json(_prisma_lifecycle_fast_health_payload(self.path, public=not self._is_local_request()))
            except Exception as exc:
                self._send_json({"ok": False, "status": "LIFECYCLE_FAST_HEALTH_ERROR", "error": str(exc)}, status=500)
            return
        # PRISMA_LIFEBOOM2_FAST_HEALTH_ROUTE_END
        # PRISMA_DATA_LIFECYCLE_ROUTE_BEGIN
        if self.path.startswith("/api/lifecycle"):
            try:
                if _prisma_lifecycle_payload is None:
                    self._send_json({"ok": False, "status": "LIFECYCLE_UNAVAILABLE"}, status=503)
                else:
                    self._send_json(_prisma_lifecycle_payload(self.path, public=not self._is_local_request()))
            except Exception as exc:
                self._send_json({"ok": False, "status": "LIFECYCLE_ERROR", "error": str(exc)}, status=500)
            return
        # PRISMA_DATA_LIFECYCLE_ROUTE_END
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
        if self.path in {"/", "/prismo", "/prismo/"}:
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
            panel_status = int(getattr(response, "status", 200))
            html = response.read(300000).decode("utf-8", errors="ignore")
        with urllib.request.urlopen(f"http://127.0.0.1:{CONTROL_CENTER_PORT}/api/health", timeout=5) as response:
            health_status_code = int(getattr(response, "status", 200))
            health = json.loads(response.read(200000).decode("utf-8", errors="ignore"))
        public_request = urllib.request.Request(
            f"http://127.0.0.1:{CONTROL_CENTER_PORT}/api/health",
            headers={"Host": "control.hitechrts.com"},
        )
        with urllib.request.urlopen(public_request, timeout=5) as response:
            public_status_code = int(getattr(response, "status", 200))
            public_health = json.loads(response.read(200000).decode("utf-8", errors="ignore"))
            public_text = json.dumps(public_health, ensure_ascii=False)
        sensitive_hits = [
            needle
            for needle in ["commandLine", "executablePath", "<LOCAL_PATH>", "<LOCAL_PATH>", "credentials-file", "token", "secret"]
            if needle.lower() in public_text.lower()
        ]
        html_ok = ("PRISMA Control Center" in html) or ("CONTROL CENTER PRISMA" in html) or ("Control Center" in html and "PRISMA" in html)
        public_mode = public_health.get("safetyMode")
        ok = bool(
            panel_status == 200
            and health_status_code == 200
            and public_status_code == 200
            and html_ok
            and health.get("overallStatus") in {"PASS", "DEGRADED", "EMPTY"}
            and public_mode == "PUBLIC_REDACTED"
            and not sensitive_hits
        )
        return {
            "ok": ok,
            "status": "PASS" if ok else "FAIL",
            "panelStatusCode": panel_status,
            "healthStatusCode": health_status_code,
            "publicStatusCode": public_status_code,
            "htmlBytes": len(html),
            "htmlOk": html_ok,
            "healthStatus": health.get("overallStatus"),
            "publicMode": public_mode,
            "publicSensitiveHits": sensitive_hits,
        }
    except Exception as exc:  # noqa: BLE001 - smoke returns diagnostics.
        return {"ok": False, "status": "FAIL", "error": str(exc)}
    finally:
        server.shutdown()
        server.server_close()
