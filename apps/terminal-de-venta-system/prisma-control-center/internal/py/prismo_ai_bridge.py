from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from config_loader import CONFIG_ROOT, LOG_ROOT, ensure_log_dirs
from prismo_context import build_context_packet, evidence_cards_from_context
from prismo_demo_provider import make_demo_response
from prismo_gemini_provider import GeminiLiveProvider
from prismo_safety import (
    _as_dict,
    _as_list,
    _as_str,
    block_if_mutation_requested,
    classify_prompt_risk,
    make_safe_error,
    sanitize_text,
    validate_response_envelope,
)


VERSION = "1.0.0"
MODES = {"ASK", "INSPECT", "IMPROVE", "EVIDENCE"}


def _bool_env(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


def prismo_settings() -> dict[str, Any]:
    key_visible = bool(os.environ.get("GEMINI_API_KEY"))
    ai_enabled = _bool_env("PRISMO_AI_ENABLED", key_visible)
    demo_mode = _bool_env("PRISMO_AI_DEMO_MODE", not key_visible)
    return {
        "key_visible": key_visible,
        "ai_enabled": ai_enabled,
        "demo_mode": demo_mode or not ai_enabled or not key_visible,
        "model": os.environ.get("PRISMO_AI_MODEL") or os.environ.get("PRISMO_GEMINI_MODEL") or "gemini-2.5-flash",
        "timeout_ms": _int_env("PRISMO_AI_TIMEOUT_MS", 30000),
        "max_input_chars": _int_env("PRISMO_AI_MAX_INPUT_CHARS", 24000),
        "max_render_blocks": _int_env("PRISMO_AI_MAX_RENDER_BLOCKS", 12),
        "html_preview_allowed": _bool_env("PRISMO_AI_ALLOW_HTML_PREVIEW", False),
    }


def _request_id() -> str:
    return "prismo_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_") + uuid.uuid4().hex[:8]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mode(value: Any) -> str:
    mode = str(value or "ASK").upper()
    return mode if mode in MODES else "ASK"


def _collect_message(payload: dict[str, Any]) -> str:
    payload = _as_dict(payload)
    return _as_str(payload.get("message") or payload.get("prompt") or payload.get("query") or "")


def _collect_evidence(payload: dict[str, Any]) -> str:
    payload = _as_dict(payload)
    chunks: list[str] = []
    if payload.get("evidenceText"):
        chunks.append(str(payload.get("evidenceText")))
    if payload.get("evidence_text"):
        chunks.append(str(payload.get("evidence_text")))
    for key in ("attachments", "clientFiles", "client_files"):
        files = _as_list(payload.get(key))
        for item in files[:8]:
            if not isinstance(item, dict):
                chunks.append(f"Attachment normalized:\n{_as_str(item)}")
                continue
            name = _as_str(item.get("name") or "attachment")
            preview = _as_str(item.get("textPreview") or item.get("text_preview") or item.get("preview") or "")
            chunks.append(f"Attachment {name}:\n{preview}")
    return "\n\n".join(chunks)


def _base_blocked_response(mode: str, request_id: str, block: dict[str, Any], input_chars: int) -> dict[str, Any]:
    block = _as_dict(block)
    safety_events = [_as_dict(event) for event in _as_list(block.get("safety_events"))]
    return {
        "ok": True,
        "status": "blocked",
        "request_id": request_id,
        "mode": mode,
        "demo_mode": prismo_settings()["demo_mode"],
        "read_only": True,
        "mutation_allowed": False,
        "blocked": True,
        "block_reason": _as_str(block.get("block_reason") or "PRISMO_V1_READ_ONLY"),
        "direct_answer": _as_str(block.get("direct_answer")),
        "certainty_level": "CONFIRMADO_POR_DOC_VIGENTE",
        "authority": {
            "winning_source": "PRISMO v1 safety firewall",
            "winning_source_type": "current_doc",
            "precedence_applied": ["PRISMO_V1_READ_ONLY", "PRISMO_SAFETY_FIREWALL"],
            "notes": "La política vigente bloquea mutaciones, ejecución, secretos y DB writes.",
        },
        "evidence": [
            {
                "id": "ev_firewall",
                "title": "Safety Firewall",
                "source_type": "doc_current",
                "summary": "PRISMO v1 sólo lee, explica y recomienda.",
                "confidence": "high",
                "freshness": "current",
            }
        ],
        "legacy_warning": {"applies": False, "legacy_sources": [], "warning": ""},
        "risk": {
            "level": "critical",
            "summary": "La petición intentó cruzar límites read-only o secreto.",
            "reasons": [_as_str(event.get("message") or event.get("code") or "") for event in safety_events],
            "mitigations": ["Generar brief o verificador seguro en lugar de ejecutar la acción."],
        },
        "safe_next_step": _as_str(block.get("safe_next_step")),
        "render_blocks": [
            {
                "id": "blocked_action",
                "type": "direct_answer_card",
                "title": "PRISMO_V1_READ_ONLY",
                "priority": "primary",
                "layout": "full",
                "safety": {
                    "trusted": False,
                    "sanitized": True,
                    "interactive": False,
                    "allows_scripts": False,
                    "allows_network": False,
                    "allows_forms": False,
                    "reason": "Blocked by PRISMO v1 safety firewall.",
                },
                "data": {"answer": _as_str(block.get("direct_answer")), "blocked": True},
            }
        ],
        "warnings": [_as_str(event.get("message") or event.get("code") or "") for event in safety_events],
        "errors": [],
        "meta": {
            "provider": "demo",
            "schema_version": "1.0.0",
            "generated_at": _now(),
            "input_chars": input_chars,
            "render_block_count": 1,
        },
    }


def _complete_meta(payload: dict[str, Any], provider: str, input_chars: int) -> dict[str, Any]:
    payload = _as_dict(payload)
    payload["meta"] = _as_dict(payload.get("meta"))
    meta = payload["meta"]
    meta.setdefault("provider", provider)
    meta.setdefault("schema_version", VERSION)
    meta.setdefault("generated_at", _now())
    meta.setdefault("input_chars", input_chars)
    meta["render_block_count"] = len(_as_list(payload.get("render_blocks")))
    return payload


def _write_ledger(response: dict[str, Any], message: str) -> None:
    try:
        response = _as_dict(response)
        risk = _as_dict(response.get("risk"))
        meta = _as_dict(response.get("meta"))
        ensure_log_dirs()
        ledger_path = LOG_ROOT / "prismo" / "ledger.jsonl"
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "ts": _now(),
            "request_id": response.get("request_id"),
            "mode": response.get("mode"),
            "status": response.get("status"),
            "promptHash": hashlib.sha256(message.encode("utf-8", errors="ignore")).hexdigest(),
            "certainty": response.get("certainty_level"),
            "riskLevel": risk.get("level"),
            "provider": meta.get("provider"),
            "demoMode": response.get("demo_mode"),
            "renderBlockCount": len(_as_list(response.get("render_blocks"))),
        }
        with ledger_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    except OSError:
        return


def prismo_status_payload(public: bool = False) -> dict[str, Any]:
    settings = prismo_settings()
    warnings: list[str] = []
    if not settings["key_visible"]:
        warnings.append("GEMINI_API_KEY no visible para este proceso; PRISMO quedó en demo mode seguro.")
    if public:
        warnings = ["PUBLIC_REDACTED_READ_ONLY"]
    config_exists = (CONFIG_ROOT / "prismo_ai_config.json").exists()
    return {
        "ok": True,
        "module": "prismo",
        "ai_enabled": bool(settings["ai_enabled"] and settings["key_visible"]),
        "demo_mode": bool(settings["demo_mode"]),
        "gemini_configured": bool(settings["key_visible"]),
        "read_only": True,
        "mutation_allowed": False,
        "html_preview_allowed": bool(settings["html_preview_allowed"]),
        "version": VERSION,
        "status": "READY" if settings["key_visible"] and not settings["demo_mode"] else "NO_API_KEY_DEMO_MODE",
        "mode": "READ_ONLY_V1",
        "gemini": {
            "configured": bool(settings["key_visible"]) if not public else False,
            "model": settings["model"],
            "fileSearchStoreConfigured": False,
            "filesApiEnabled": False,
            "contextCachingEnabled": False,
        },
        "authority": {
            "currentStateLoaded": True,
            "governanceLoaded": config_exists,
            "legacyPolicyLoaded": True,
        },
        "safety": {
            "mutationAllowed": False,
            "functionCallingAllowed": False,
            "frontendKeyExposureAllowed": False,
        },
        "warnings": warnings,
    }


def prismo_demo_payload() -> dict[str, Any]:
    request_id = _request_id()
    context = build_context_packet("")
    response = make_demo_response("ASK", "Demo PRISMO", context, request_id)
    response["meta"]["generated_at"] = _now()
    validated, _errors = validate_response_envelope(response)
    return _complete_meta(validated, "demo", len("Demo PRISMO"))


def _prismo_query_payload_impl(payload: dict[str, Any], public: bool = False) -> dict[str, Any]:
    request_id = _request_id()
    settings = prismo_settings()
    started = time.perf_counter()
    if public:
        return {
            "ok": False,
            "status": "blocked",
            "request_id": request_id,
            "mode": "ASK",
            "demo_mode": True,
            "read_only": True,
            "mutation_allowed": False,
            "blocked": True,
            "block_reason": "PUBLIC_REDACTED_READ_ONLY",
            "direct_answer": "Bloqueado: PRISMO query v1 sólo acepta consultas locales para proteger evidencia interna.",
            "certainty_level": "CONFIRMADO_POR_DOC_VIGENTE",
            "authority": {"winning_source": "PRISMO public safety policy", "winning_source_type": "current_doc", "precedence_applied": ["local-only query"], "notes": "Status público redacted; query local-only."},
            "evidence": [],
            "risk": {"level": "critical", "summary": "Consulta pública bloqueada.", "reasons": ["Local-only."], "mitigations": ["Abrir Control Center local."]},
            "safe_next_step": "Consulta PRISMO desde 127.0.0.1.",
            "render_blocks": [],
            "warnings": ["PUBLIC_REDACTED_READ_ONLY"],
            "errors": [],
            "meta": {"provider": "demo", "schema_version": VERSION, "generated_at": _now(), "input_chars": 0, "render_block_count": 0},
        }

    if not isinstance(payload, dict):
        payload = {}
    mode = _mode(payload.get("mode"))
    message_raw = _collect_message(payload)
    evidence_raw = _collect_evidence(payload)
    message, message_events = sanitize_text(message_raw, max_chars=settings["max_input_chars"])
    evidence, evidence_events = sanitize_text(evidence_raw, max_chars=250000)
    input_chars = len(message) + len(evidence)
    prompt_events = classify_prompt_risk(message + "\n" + evidence)
    block = block_if_mutation_requested(message)
    if block:
        response = _base_blocked_response(mode, request_id, block, input_chars)
        validated, _errors = validate_response_envelope(response)
        _write_ledger(validated, message)
        return validated

    context = build_context_packet(evidence)
    context.setdefault("safetyEvents", [])
    context["safetyEvents"].extend(message_events + evidence_events + prompt_events)
    warnings = [_as_str(_as_dict(event).get("message") or _as_dict(event).get("code") or "") for event in context["safetyEvents"]]
    response: dict[str, Any] | None = None
    provider = "demo"
    provider_errors: list[dict[str, Any]] = []

    if settings["ai_enabled"] and not settings["demo_mode"] and settings["key_visible"]:
        provider = "gemini"
        live = GeminiLiveProvider(model=settings["model"], timeout_ms=settings["timeout_ms"])
        response, provider_errors = live.generate(mode=mode, message=message, context=context, request_id=request_id)
        if response is None:
            provider = "demo"
            warnings.append("Gemini no respondió con JSON válido; PRISMO usó demo fallback seguro.")

    if response is None:
        if not settings["key_visible"]:
            warnings.append("GEMINI_API_KEY no visible para este proceso; PRISMO quedó en demo mode seguro.")
        response = make_demo_response(mode, message, context, request_id, warnings=warnings)

    response = _as_dict(response)
    response.setdefault("request_id", request_id)
    response.setdefault("mode", mode)
    response.setdefault("demo_mode", provider == "demo")
    response.setdefault("read_only", True)
    response.setdefault("mutation_allowed", False)
    response.setdefault("evidence", evidence_cards_from_context(context))
    response["warnings"] = [_as_str(item) for item in _as_list(response.get("warnings"))] + warnings
    response["errors"] = _as_list(response.get("errors")) + provider_errors
    response.setdefault("authority", {"winning_source": "NO_CONFIRMADO", "winning_source_type": "unknown", "precedence_applied": context.get("authorityRules", []), "notes": "No authority source provided by provider."})
    response.setdefault("risk", {"level": "medium", "summary": "Respuesta degradada por falta de evidencia.", "reasons": [], "mitigations": ["Reunir contexto current."]})
    response.setdefault("safe_next_step", "Reunir evidencia current y ejecutar verificador seguro.")
    response.setdefault("certainty_level", "NO_CONFIRMADO")
    response.setdefault("direct_answer", "No hay evidencia suficiente para confirmar una respuesta.")
    response["meta"] = _as_dict(response.get("meta"))
    response["meta"]["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    validated, _errors = validate_response_envelope(response)
    _complete_meta(validated, provider, input_chars)
    _write_ledger(validated, message)
    return validated


# PRISMO_QUERY_NULL_GUARD_BEGIN
def _prismo_query_emergency_response(payload: dict[str, Any] | None, public: bool, code: str, detail: str) -> dict[str, Any]:
    request_id = _request_id()
    settings = prismo_settings()
    if isinstance(payload, dict):
        mode = _mode(payload.get("mode"))
        message = _collect_message(payload)
    else:
        mode = "ASK"
        message = ""
    provider = "gemini" if settings.get("ai_enabled") and not settings.get("demo_mode") and settings.get("key_visible") else "demo"
    error = make_safe_error(
        code,
        detail,
        "PRISMO devolvió un error seguro estructurado. No se ejecutó ninguna acción.",
        recoverable=True,
    )
    response: dict[str, Any] = {
        "ok": False,
        "status": "error",
        "request_id": request_id,
        "mode": mode,
        "demo_mode": provider == "demo",
        "read_only": True,
        "mutation_allowed": False,
        "direct_answer": "PRISMO no pudo completar la consulta, pero evitó devolver null y mantuvo el contrato seguro.",
        "certainty_level": "NO_CONFIRMADO",
        "authority": {
            "winning_source": "prismo_ai_bridge.py",
            "winning_source_type": "code",
            "precedence_applied": ["runtime_guard", "schema_guard", "read_only_v1"],
            "notes": "El bridge atrapó una salida inválida o excepción y devolvió JSON seguro."
        },
        "evidence": [],
        "legacy_warning": {"applies": False, "legacy_sources": [], "warning": ""},
        "risk": {
            "level": "medium",
            "summary": "La respuesta live no pudo completarse como éxito validado.",
            "reasons": [error["safe_message"], error["code"]],
            "mitigations": [
                "Mantener respuesta estructurada.",
                "Revisar logs sanitizados.",
                "No tratar la consulta como confirmación factual si no hay evidencia."
            ],
        },
        "safe_next_step": "Reintentar la consulta o revisar el reporte PRISMO en <LOCAL_PATH>",
        "render_blocks": [
            {
                "id": "prismo_query_safe_error",
                "type": "direct_answer_card",
                "title": "Consulta protegida",
                "priority": "primary",
                "layout": "full",
                "safety": {
                    "trusted": False,
                    "sanitized": True,
                    "interactive": False,
                    "allows_scripts": False,
                    "allows_network": False,
                    "allows_forms": False,
                    "reason": "PRISMO query null guard."
                },
                "data": {
                    "answer": "El endpoint respondió con error seguro estructurado en vez de null.",
                    "code": error["code"]
                }
            }
        ],
        "warnings": ["PRISMO_QUERY_NULL_GUARD_BRIDGE"],
        "errors": [error],
        "meta": {
            "provider": provider,
            "model": settings.get("model"),
            "schema_version": VERSION,
            "generated_at": _now(),
            "input_chars": len(message or ""),
            "render_block_count": 1
        },
    }
    try:
        validated, _errors = validate_response_envelope(response)
        _complete_meta(validated, provider, len(message or ""))
        _write_ledger(validated, message or "")
        return validated
    except Exception:
        return response


def prismo_query_payload(payload: dict[str, Any], public: bool = False) -> dict[str, Any]:
    try:
        result = _prismo_query_payload_impl(payload, public=public)
        if isinstance(result, dict):
            return result
        return _prismo_query_emergency_response(
            payload if isinstance(payload, dict) else {},
            public,
            "PRISMO_QUERY_RETURNED_NON_OBJECT",
            f"prismo_query_payload implementation returned {type(result).__name__}",
        )
    except Exception as exc:  # noqa: BLE001 - endpoint must never return null or raw stack trace.
        return _prismo_query_emergency_response(
            payload if isinstance(payload, dict) else {},
            public,
            "PRISMO_QUERY_EXCEPTION",
            str(exc),
        )
# PRISMO_QUERY_NULL_GUARD_END
