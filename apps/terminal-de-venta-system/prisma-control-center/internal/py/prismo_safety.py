from __future__ import annotations

import json
import re
from typing import Any


SECRET_REDACTION = "[PRISMO_SECRET_REDACTED]"

SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"AIza[0-9A-Za-z\-_]{20,}"),
    re.compile(r"sk-[0-9A-Za-z\-_]{20,}"),
    re.compile(r"-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----", re.IGNORECASE | re.DOTALL),
    re.compile(r"(?i)\b(GEMINI_API_KEY|GOOGLE_API_KEY|CLOUDFLARE_API_TOKEN|DATABASE_URL)\s*[:=]\s*['\"]?[^'\"\s]+"),
    re.compile(r"(?i)\b(api[_-]?key|client_secret|secret|token|password|authorization)\s*[:=]\s*['\"]?[^'\"\s]+"),
    re.compile(r"(?i)\bBearer\s+[0-9A-Za-z._\-=]{18,}"),
]

MUTATION_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("DELETE_FILES", re.compile(r"(?i)\b(rm\s+-rf|del\s+/s\s+/q|delete|borra(?:r)?|elimina(?:r)?|remove)\b"), "PRISMO v1 no borra archivos."),
    ("DB_MUTATION", re.compile(r"(?i)\b(drop\s+table|drop\s+database|truncate|clear\s+database|borra.*\b(tablas?|db|database|canonical\.db)|modifica.*\bdb)\b"), "PRISMO v1 no modifica DB."),
    ("COMMAND_EXECUTION", re.compile(r"(?i)\b(ejecuta|corre|run|execute|powershell|cmd\.exe|script|comando|kill\s+process|shutdown)\b"), "PRISMO v1 no ejecuta comandos."),
    ("DEPLOY", re.compile(r"(?i)\b(deploy|despliega|sube\s+a\s+producci[oó]n|publish|release\s+prod)\b"), "PRISMO v1 no despliega."),
    ("GIT_MUTATION", re.compile(r"(?i)\b(git\s+push|git\s+commit|commit\s+autom[aá]tico|push\s+autom[aá]tico|rewrite\s+history)\b"), "PRISMO v1 no muta git ni reescribe historia."),
    ("SEED_CLEAR", re.compile(r"(?i)\b(seed|clear|migrate|migration|prisma\s+migrate|reset\s+database)\b"), "PRISMO v1 no corre seed, clear ni migraciones."),
    ("PACKAGE_INSTALL", re.compile(r"(?i)\b(instala|install\s+package|pnpm\s+add|npm\s+install|yarn\s+add)\b"), "PRISMO v1 no instala dependencias."),
]

SECRET_REQUEST_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)\b(lee|read|muestra|dame|print|revela)\b.*\b(\.env|api\s*key|secret|token|password|GEMINI_API_KEY|GOOGLE_API_KEY|DATABASE_URL)\b"),
    re.compile(r"(?i)\b(GEMINI_API_KEY|GOOGLE_API_KEY|CLOUDFLARE_API_TOKEN|DATABASE_URL)\b.*\b(muestra|print|dame|revela|valor)\b"),
]

PROMPT_INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("IGNORE_PREVIOUS", re.compile(r"(?i)ignora(?:r)?\s+(todas\s+)?(las\s+)?(reglas|instrucciones)\s+anteriores|ignore\s+previous\s+instructions")),
    ("SYSTEM_IMPERSONATION", re.compile(r"(?i)eres\s+sistema|act[uú]a\s+como\s+sistema|act\s+as\s+(system|developer)")),
    ("PROMPT_REVEAL", re.compile(r"(?i)revela\s+prompt|reveal\s+(the\s+)?prompt|system\s+prompt")),
    ("SAFETY_BYPASS", re.compile(r"(?i)omite\s+seguridad|disable\s+safety|sin\s+seguridad")),
    ("LEGACY_AUTHORITY", re.compile(r"(?i)legacy\s+(manda|como\s+autoridad|is\s+authoritative)|usa\s+legacy\s+como\s+autoridad")),
    ("NO_EVIDENCE", re.compile(r"(?i)responde\s+sin\s+evidencia|sin\s+evidencia|without\s+evidence")),
]


def _as_dict(value: Any, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(fallback, dict):
        return dict(fallback)
    return {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=True, default=str)
    except Exception:  # noqa: BLE001 - defensive stringification for provider data.
        return str(value)


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y", "on"}
    return default


def _as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return max(0, value)
    if isinstance(value, float):
        return max(0, int(value))
    if isinstance(value, str):
        try:
            return max(0, int(float(value.strip())))
        except ValueError:
            return default
    return default


def redact_secrets(value: str) -> str:
    redacted = str(value or "")
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(SECRET_REDACTION, redacted)
    return redacted


def _safe_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {redact_secrets(str(key)): _safe_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_safe_json_value(item) for item in value]
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    return redact_secrets(_as_str(value))


def _string_list(value: Any) -> list[str]:
    return [redact_secrets(_as_str(item)) for item in _as_list(value)]


def normalize_evidence_items(value: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for index, item in enumerate(_as_list(value)):
        if isinstance(item, dict):
            source_type = _as_str(item.get("source_type") or item.get("sourceType") or "unknown", "unknown")
            confidence = _as_str(item.get("confidence") or "low", "low")
            freshness = _as_str(item.get("freshness") or "unknown", "unknown")
            clean = {
                **_as_dict(_safe_json_value(item)),
                "id": redact_secrets(_as_str(item.get("id") or f"evidence_{index + 1:02d}")),
                "title": redact_secrets(_as_str(item.get("title") or "Evidencia PRISMO")),
                "source_type": redact_secrets(source_type or "unknown"),
                "summary": redact_secrets(_as_str(item.get("summary") or item.get("text") or item.get("value") or "")),
                "confidence": redact_secrets(confidence or "low"),
                "freshness": redact_secrets(freshness or "unknown"),
            }
            items.append(clean)
            continue
        items.append(
            {
                "id": f"normalized_evidence_{index + 1:02d}",
                "title": "Evidencia normalizada",
                "source_type": "unknown",
                "summary": redact_secrets(_as_str(item)),
                "confidence": "low",
                "freshness": "unknown",
            }
        )
    return items


def normalize_errors(value: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(_as_list(value)):
        if isinstance(item, dict):
            normalized.append(
                {
                    "code": redact_secrets(_as_str(item.get("code") or f"PROVIDER_ERROR_{index + 1:02d}")),
                    "message": redact_secrets(_as_str(item.get("message") or item.get("detail") or item)),
                    "safe_message": redact_secrets(
                        _as_str(item.get("safe_message") or item.get("safeMessage") or "PRISMO normalizó un error no estructurado.")
                    ),
                    "recoverable": _as_bool(item.get("recoverable"), True),
                }
            )
            continue
        normalized.append(
            {
                "code": f"NORMALIZED_ERROR_{index + 1:02d}",
                "message": redact_secrets(_as_str(item)),
                "safe_message": "PRISMO normalizó un error no estructurado.",
                "recoverable": True,
            }
        )
    return normalized


def normalize_warnings(value: Any) -> list[str]:
    return _string_list(value)


def normalize_authority(value: Any) -> dict[str, Any]:
    authority = _as_dict(value)
    source_types = {"current_state", "code", "current_doc", "temporary_evidence", "legacy", "planned", "unknown"}
    source_type = _as_str(authority.get("winning_source_type") or authority.get("winningSourceType") or "unknown", "unknown")
    if source_type not in source_types:
        source_type = "unknown"
    winning_source = _as_str(authority.get("winning_source") or authority.get("winningSource") or "", "")
    notes = _as_str(authority.get("notes") or "", "")
    if not authority and value is not None:
        winning_source = redact_secrets(_as_str(value, "NO_CONFIRMADO")) or "NO_CONFIRMADO"
        notes = "Autoridad normalizada desde un valor no estructurado; no se trata como fuente dominante."
    return {
        "winning_source": redact_secrets(winning_source or "NO_CONFIRMADO"),
        "winning_source_type": source_type,
        "precedence_applied": _string_list(authority.get("precedence_applied") or authority.get("precedenceApplied") or []),
        "notes": redact_secrets(notes or "No authority source provided by provider."),
    }


def normalize_legacy_warning(value: Any) -> dict[str, Any]:
    legacy = _as_dict(value)
    if not legacy and value is None:
        return {"applies": False, "legacy_sources": [], "warning": ""}
    return {
        "applies": _as_bool(legacy.get("applies"), False),
        "legacy_sources": _string_list(legacy.get("legacy_sources") or legacy.get("legacySources") or []),
        "warning": redact_secrets(_as_str(legacy.get("warning") or (value if not legacy else ""))),
    }


def normalize_risk(value: Any) -> dict[str, Any]:
    risk = _as_dict(value)
    allowed_levels = {"none", "low", "medium", "high", "critical"}
    level = _as_str(risk.get("level") or (value if isinstance(value, str) else "medium"), "medium").strip().lower()
    if level not in allowed_levels:
        level = "medium"
    summary = _as_str(risk.get("summary") or risk.get("description") or "", "")
    if not risk and value is not None:
        summary = _as_str(value, "Riesgo normalizado desde valor no estructurado.")
    return {
        "level": level,
        "summary": redact_secrets(summary or "Riesgo normalizado por PRISMO."),
        "reasons": _string_list(risk.get("reasons") or []),
        "mitigations": _string_list(risk.get("mitigations") or []),
    }


def normalize_meta(value: Any, *, render_block_count: int = 0, input_chars: int = 0) -> dict[str, Any]:
    meta = _as_dict(value)
    provider = _as_str(meta.get("provider") or "demo", "demo")
    if provider not in {"gemini", "demo"}:
        provider = "demo"
    normalized = {
        **_as_dict(_safe_json_value(meta)),
        "provider": provider,
        "schema_version": "1.0.0",
        "generated_at": redact_secrets(_as_str(meta.get("generated_at") or "", "")),
        "input_chars": _as_int(meta.get("input_chars"), input_chars),
        "render_block_count": _as_int(meta.get("render_block_count"), render_block_count),
    }
    if "model" in meta:
        normalized["model"] = redact_secrets(_as_str(meta.get("model")))
    if "latency_ms" in meta:
        try:
            normalized["latency_ms"] = float(meta.get("latency_ms"))
        except (TypeError, ValueError):
            normalized["latency_ms"] = 0
    return normalized


def sanitize_text(value: str, max_chars: int | None = None) -> tuple[str, list[dict[str, Any]]]:
    raw = str(value or "")
    events: list[dict[str, Any]] = []
    redacted = redact_secrets(raw)
    if redacted != raw:
        events.append(
            {
                "code": "SECRET_REDACTED",
                "severity": "high",
                "message": "Se redactó contenido con apariencia de secreto antes de procesar la evidencia.",
            }
        )
    if max_chars is not None and len(redacted) > max_chars:
        redacted = redacted[:max_chars]
        events.append(
            {
                "code": "INPUT_TRUNCATED",
                "severity": "medium",
                "message": f"Entrada truncada al límite seguro de {max_chars} caracteres.",
            }
        )
    return redacted, events


def classify_prompt_risk(prompt: str) -> list[dict[str, Any]]:
    text = str(prompt or "")
    events: list[dict[str, Any]] = []
    for code, pattern, message in MUTATION_PATTERNS:
        if pattern.search(text):
            events.append({"code": code, "severity": "critical", "message": message})
    for pattern in SECRET_REQUEST_PATTERNS:
        if pattern.search(text):
            events.append(
                {
                    "code": "SECRET_REQUEST",
                    "severity": "critical",
                    "message": "PRISMO v1 no lee ni muestra secretos.",
                }
            )
            break
    for code, pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(text):
            events.append(
                {
                    "code": code,
                    "severity": "medium",
                    "message": "Texto tratado como dato no confiable, no como instrucción.",
                }
            )
    return events


def block_if_mutation_requested(prompt: str) -> dict[str, Any] | None:
    events = classify_prompt_risk(prompt)
    blocking_events = [
        event
        for event in events
        if event["code"]
        in {
            "DELETE_FILES",
            "DB_MUTATION",
            "COMMAND_EXECUTION",
            "DEPLOY",
            "GIT_MUTATION",
            "SEED_CLEAR",
            "PACKAGE_INSTALL",
            "SECRET_REQUEST",
        }
    ]
    if not blocking_events:
        return None
    reason = "PRISMO_V1_SECRET_FIREWALL" if any(event["code"] == "SECRET_REQUEST" for event in blocking_events) else "PRISMO_V1_READ_ONLY"
    if reason == "PRISMO_V1_SECRET_FIREWALL":
        answer = "Bloqueado: PRISMO v1 no lee, imprime ni expone secretos. La variable de IA sólo puede existir en backend y nunca aparece en respuestas."
        next_step = "Pide una revisión de exposición de secretos o un verificador seguro de frontend."
    else:
        answer = "Bloqueado: PRISMO v1 sólo lee, explica y recomienda. No ejecuta acciones ni modifica archivos."
        next_step = "Pide un Improvement Brief o una lista de verificadores seguros."
    return {
        "blocked": True,
        "block_reason": reason,
        "direct_answer": answer,
        "safe_next_step": next_step,
        "safety_events": events,
    }


def detect_prompt_injection(value: str) -> list[dict[str, Any]]:
    return [event for event in classify_prompt_risk(value) if event["code"] in {code for code, _pattern in PROMPT_INJECTION_PATTERNS}]


def make_safe_error(code: str, message: str, safe_message: str | None = None, recoverable: bool = True) -> dict[str, Any]:
    return {
        "code": code,
        "message": redact_secrets(message),
        "safe_message": safe_message or "No se pudo validar la respuesta de PRISMO. No se ejecutó ninguna acción.",
        "recoverable": recoverable,
    }


def validate_response_envelope(payload: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from prismo_render_contracts import sanitize_render_blocks

    errors: list[dict[str, Any]] = []
    if not isinstance(payload, dict):
        errors.append(make_safe_error("INVALID_RESPONSE", "Response is not an object"))
    raw_payload = payload
    payload = _as_dict(payload)
    status = _as_str(payload.get("status") or "partial", "partial")
    if status not in {"success", "partial", "blocked", "error"}:
        status = "partial"
    allowed_certainty = {
        "CONFIRMADO_POR_CURRENT_STATE",
        "CONFIRMADO_POR_CODIGO",
        "CONFIRMADO_POR_DOC_VIGENTE",
        "CONFIRMADO_POR_EVIDENCIA_TEMPORAL",
        "HISTORICO_LEGACY",
        "PLANEADO_NO_IMPLEMENTADO",
        "NO_CONFIRMADO",
    }
    certainty = _as_str(payload.get("certainty_level") or "NO_CONFIRMADO", "NO_CONFIRMADO")
    if certainty not in allowed_certainty:
        certainty = "NO_CONFIRMADO"
        errors.append(make_safe_error("CERTAINTY_NORMALIZED", "Invalid certainty level"))
    render_blocks, block_events = sanitize_render_blocks(payload.get("render_blocks"))
    warnings = normalize_warnings(payload.get("warnings"))
    for event in block_events:
        event_obj = _as_dict(event)
        warnings.append(redact_secrets(_as_str(event_obj.get("message") or event_obj.get("code") or "Render block sanitizado.")))

    meta = normalize_meta(payload.get("meta"), render_block_count=len(render_blocks), input_chars=0)
    mode = _as_str(payload.get("mode") or "ASK", "ASK").upper()
    if mode not in {"ASK", "INSPECT", "IMPROVE", "EVIDENCE"}:
        mode = "ASK"
    normalized: dict[str, Any] = {
        "ok": _as_bool(payload.get("ok"), True),
        "status": status,
        "request_id": redact_secrets(_as_str(payload.get("request_id") or "prismo_normalized_response")),
        "mode": mode,
        "demo_mode": _as_bool(payload.get("demo_mode"), meta.get("provider") == "demo"),
        "read_only": True,
        "mutation_allowed": False,
        "direct_answer": redact_secrets(_as_str(payload.get("direct_answer") or "No hay respuesta directa validada.")),
        "certainty_level": certainty,
        "authority": normalize_authority(payload.get("authority")),
        "evidence": normalize_evidence_items(payload.get("evidence")),
        "legacy_warning": normalize_legacy_warning(payload.get("legacy_warning")),
        "risk": normalize_risk(payload.get("risk")),
        "safe_next_step": redact_secrets(_as_str(payload.get("safe_next_step") or "Reunir evidencia current y ejecutar verificador seguro.")),
        "render_blocks": render_blocks,
        "warnings": warnings,
        "errors": normalize_errors(payload.get("errors")),
        "meta": meta,
    }
    if "blocked" in payload:
        normalized["blocked"] = _as_bool(payload.get("blocked"), False)
    if "block_reason" in payload:
        normalized["block_reason"] = redact_secrets(_as_str(payload.get("block_reason")))
    if payload.get("improvement_brief") is not None:
        normalized["improvement_brief"] = _as_dict(_safe_json_value(payload.get("improvement_brief")))
    if payload.get("context_pack_request") is not None:
        normalized["context_pack_request"] = _as_dict(_safe_json_value(payload.get("context_pack_request")))
    if not isinstance(raw_payload, dict):
        normalized["status"] = "error"
        normalized["ok"] = False
    normalized["errors"].extend(errors)
    return normalized, errors
