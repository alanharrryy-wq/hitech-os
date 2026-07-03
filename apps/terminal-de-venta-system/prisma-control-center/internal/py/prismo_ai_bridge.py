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
try:
    from prismo_app_live_context import app_live_context_payload as _prismo_app_live_context_payload
except Exception:  # noqa: BLE001 - optional read-only adapter.
    _prismo_app_live_context_payload = None
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
GUIDANCE_INTENTS = {
    "diagnose": "Diagnose",
    "explain": "Explain",
    "recommend": "Recommend",
    "compare": "Compare",
    "audit": "Audit",
    "prepare_action": "Prepare action",
    "summarize": "Summarize",
    "investigate": "Investigate",
}
GUIDANCE_AREAS = {
    "learning": "Learning",
    "sync": "Sync",
    "pc_ui": "PC UI",
    "tablet": "Tablet",
    "pos": "POS",
    "chart_lab": "Chart Lab",
    "governance": "Governance",
    "evidence_vault": "Evidence Vault",
    "protocols": "Protocols",
    "visual_theater": "Visual/Theater",
}
GUIDANCE_LENSES = {
    "recent_evidence": "Recent evidence",
    "detected_patterns": "Detected patterns",
    "suggested_protocols": "Suggested protocols",
    "procedural_memory": "Procedural memory",
    "runtime_state": "Runtime state",
    "governance_canon": "Governance canon",
    "visual_memory": "Visual memory",
    "operational_memory": "Operational memory",
}
RESPONSE_CHAIN = ["question", "interpretation", "protocol", "evidence", "result", "feedback"]


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


def _slug(value: Any) -> str:
    text = _as_str(value).strip().lower()
    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = "_".join(part for part in text.split() if part)
    aliases = {
        "prepare": "prepare_action",
        "prepare_action": "prepare_action",
        "pc": "pc_ui",
        "pc_ui": "pc_ui",
        "visual": "visual_theater",
        "theater": "visual_theater",
        "visual_theater": "visual_theater",
        "evidence": "evidence_vault",
        "evidence_vault": "evidence_vault",
        "chart": "chart_lab",
        "chart_lab": "chart_lab",
        "recent": "recent_evidence",
        "patterns": "detected_patterns",
        "protocol": "suggested_protocols",
        "protocols": "protocols",
        "procedural": "procedural_memory",
        "runtime": "runtime_state",
        "governance": "governance",
        "canon": "governance_canon",
        "visual_memory": "visual_memory",
        "operational": "operational_memory",
    }
    return aliases.get(text, text)


def _guidance_value(payload: dict[str, Any], key: str, allowed: dict[str, str]) -> tuple[str | None, str]:
    payload = _as_dict(payload)
    source_map = _as_dict(payload.get("selection_source"))
    raw = payload.get(key)
    guidance = _as_dict(payload.get("guidance"))
    if raw is None:
        raw = guidance.get(key)
    if isinstance(raw, dict):
        raw = raw.get("value") or raw.get("id") or raw.get("label")
    slug = _slug(raw)
    if slug in allowed:
        source = _as_str(source_map.get(key) or "user")
        return slug, source if source in {"user", "inferred", "unset", "mixed"} else "user"
    return None, "unset"


def _infer_from_keywords(text: str, options: list[tuple[str, list[str]]], fallback: str) -> str:
    low = text.lower()
    for value, words in options:
        if any(word in low for word in words):
            return value
    return fallback


def _infer_interpretation(payload: dict[str, Any], query: str, base_response: dict[str, Any] | None = None) -> dict[str, Any]:
    base_response = _as_dict(base_response)
    intent, intent_source = _guidance_value(payload, "intent", GUIDANCE_INTENTS)
    area, area_source = _guidance_value(payload, "area", GUIDANCE_AREAS)
    lens, lens_source = _guidance_value(payload, "lens", GUIDANCE_LENSES)
    text = " ".join([query, _collect_evidence(payload), _as_str(base_response.get("direct_answer"))])

    if not intent:
        intent = _infer_from_keywords(
            text,
            [
                ("diagnose", ["error", "fail", "falla", "bloque", "diagn", "causa", "502", "404"]),
                ("compare", ["compar", "versus", " vs ", "diferencia"]),
                ("audit", ["audit", "verifica", "review", "riesgo", "gate"]),
                ("prepare_action", ["accion", "action", "rollback", "runbook", "prepara"]),
                ("summarize", ["resume", "summary", "brief", "resumen"]),
                ("recommend", ["recomienda", "recommend", "siguiente", "prioridad"]),
                ("investigate", ["investiga", "trace", "rastre", "evidencia"]),
                ("explain", ["explica", "why", "porque", "por que"]),
            ],
            "diagnose",
        )
        intent_source = "inferred"

    if not area:
        area = _infer_from_keywords(
            text,
            [
                ("learning", ["learning", "memoria", "memory", "miner", "authority"]),
                ("sync", ["sync", "sincron", "outbox", "ingest"]),
                ("pc_ui", ["pc", "backoffice", "desktop"]),
                ("tablet", ["tablet"]),
                ("pos", ["pos", "venta", "ticket"]),
                ("chart_lab", ["chart", "graf", "echarts"]),
                ("governance", ["govern", "canon", "policy", "seguridad"]),
                ("evidence_vault", ["evidence", "evidencia", "vault"]),
                ("protocols", ["protocol", "protocolo"]),
                ("visual_theater", ["visual", "theater", "teatro", "glass", "cloudglass"]),
            ],
            "learning",
        )
        area_source = "inferred"

    if not lens:
        lens = _infer_from_keywords(
            text,
            [
                ("procedural_memory", ["protocol", "pasos", "fix", "repair", "procedural"]),
                ("recent_evidence", ["recent", "actual", "current", "evidencia"]),
                ("detected_patterns", ["pattern", "patron", "miner"]),
                ("suggested_protocols", ["recommend", "protocolo", "protocol"]),
                ("runtime_state", ["runtime", "estado", "health", "status"]),
                ("governance_canon", ["govern", "canon", "policy"]),
                ("visual_memory", ["visual", "glass", "cloudglass", "refrigerant"]),
                ("operational_memory", ["operational", "operativo", "control center"]),
            ],
            "procedural_memory",
        )
        lens_source = "inferred"

    sources = {intent_source, area_source, lens_source}
    confidence = 0.86 if sources == {"user"} else 0.72 if "user" in sources else 0.64
    source = "user" if sources == {"user"} else "inferred" if sources == {"inferred"} else "mixed"
    chips = [
        {"key": "intent", "value": intent, "label": GUIDANCE_INTENTS[intent], "source": intent_source, "editable": True},
        {"key": "area", "value": area, "label": GUIDANCE_AREAS[area], "source": area_source, "editable": True},
        {"key": "lens", "value": lens, "label": GUIDANCE_LENSES[lens], "source": lens_source, "editable": True},
    ]
    return {
        "intent": intent,
        "area": area,
        "lens": lens,
        "confidence": round(confidence, 2),
        "source": source,
        "chips": chips,
        "rationale": "PRISMO normalized user guidance when present and inferred missing intent, area, and lens from the free-text query, evidence, runtime state, and governance constraints.",
    }


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


def prismo_tools_status_payload(public: bool = False) -> dict[str, Any]:
    warnings: list[str] = []
    if public:
        warnings.append("PUBLIC_REDACTED_READ_ONLY")
    return {
        "ok": True,
        "read_only": True,
        "mutation_allowed": False,
        "tools": [],
        "evidence": [],
        "warnings": warnings,
        "meta": {
            "source": "local_read_only_detection",
            "generated_at": _now(),
            "public": bool(public),
        },
    }


def _learning_snapshot(query: str) -> tuple[dict[str, Any], list[str]]:
    missing: list[str] = []
    snapshot: dict[str, Any] = {
        "status": {},
        "recommendation": {},
        "insights": {},
        "feedback_stats": {},
        "technical_drawer": {},
    }
    try:
        from prismo_learning.api import (  # noqa: PLC0415 - optional local adapter import.
            learning_feedback_stats_payload,
            learning_insights_payload,
            learning_recommend_protocol_payload,
            learning_status_payload,
            learning_technical_drawer_payload,
        )

        snapshot["status"] = learning_status_payload(public=False)
        snapshot["recommendation"] = learning_recommend_protocol_payload(query=query, public=False)
        snapshot["insights"] = learning_insights_payload(public=False)
        snapshot["feedback_stats"] = learning_feedback_stats_payload(public=False)
        snapshot["technical_drawer"] = learning_technical_drawer_payload(public=False)
    except Exception as exc:  # noqa: BLE001 - theater must remain recoverable.
        missing.append(f"prismo_learning.api:{type(exc).__name__}")
    return snapshot, missing


def _block_contract(block_id: str, block_type: str, title: str, summary: str, priority: int, data: dict[str, Any] | None = None, tone: str = "neutral", collapsible: bool = False) -> dict[str, Any]:
    return {
        "id": block_id,
        "type": block_type,
        "title": title,
        "summary": summary,
        "message": summary,
        "priority": priority,
        "status": "ready",
        "tone": tone,
        "data": data or {},
        "actions": [],
        "collapsible": collapsible,
        "layout": "full" if priority <= 20 or block_type in {"hero_response", "technical_drawer"} else "half",
        "safety": {
            "trusted": False,
            "sanitized": True,
            "interactive": block_type in {"action_bar", "feedback_dock", "technical_drawer"},
            "allows_scripts": False,
            "allows_network": False,
            "allows_forms": False,
            "reason": "PRISMO Theater block contract generated server-side from sanitized runtime data.",
        },
    }


def _evidence_summary(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(evidence[:8]):
        item = _as_dict(item)
        rows.append({
            "id": _as_str(item.get("id") or f"evidence_{index + 1}"),
            "title": _as_str(item.get("title") or "Evidence"),
            "summary": _as_str(item.get("summary") or item.get("quote") or ""),
            "source_type": _as_str(item.get("source_type") or "runtime"),
            "freshness": _as_str(item.get("freshness") or "current"),
            "confidence": _as_str(item.get("confidence") or "medium"),
            "relevance": "high" if index < 3 else "supporting",
        })
    return rows


def _selected_protocols(snapshot: dict[str, Any], interpretation: dict[str, Any]) -> list[dict[str, Any]]:
    recommendation = _as_dict(snapshot.get("recommendation"))
    raw = _as_list(recommendation.get("selected_protocols") or recommendation.get("protocols"))
    protocols: list[dict[str, Any]] = []
    for index, item in enumerate(raw[:5]):
        if isinstance(item, dict):
            label = _as_str(item.get("name") or item.get("id") or item.get("label") or f"protocol_{index + 1}")
            score = item.get("score") if isinstance(item.get("score"), (int, float)) else round(0.86 - index * 0.08, 2)
            reason = _as_str(item.get("reason") or item.get("summary") or "Matched by PRISMO Learning recommendation engine.")
        else:
            label = _as_str(item or f"protocol_{index + 1}")
            score = round(0.86 - index * 0.08, 2)
            reason = "Matched by PRISMO Learning recommendation engine."
        protocols.append({"id": _slug(label) or f"protocol_{index + 1}", "label": label, "score": score, "reason": reason})
    if not protocols:
        protocols = [
            {
                "id": f"{interpretation.get('intent', 'diagnose')}_{interpretation.get('lens', 'procedural_memory')}",
                "label": "Adaptive diagnostic protocol",
                "score": 0.72,
                "reason": "Selected from inferred intent, area, lens, procedural memory, and governance constraints.",
            }
        ]
    return protocols


def _memory_used(snapshot: dict[str, Any], interpretation: dict[str, Any], protocols: list[dict[str, Any]], app_live: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    status = _as_dict(snapshot.get("status"))
    insights = _as_dict(snapshot.get("insights"))
    counts = {
        "evidence": status.get("evidence_count", 0),
        "patterns": status.get("pattern_count", len(_as_list(insights.get("patterns")))),
        "protocols": len(protocols),
    }
    app_live = _as_dict(app_live or {})
    summary = _as_dict(app_live.get("summary"))
    memory_layers = _as_dict(app_live.get("memory_layers"))
    evidence_library = _as_dict(app_live.get("evidence_library"))
    authority_memory = _as_dict(app_live.get("authority_memory"))
    delta = _as_dict(app_live.get("delta_scanner"))
    return [
        {"type": "semantic_memory", "summary": f"Project Brain indexed {summary.get('file_count', 0)} files, {summary.get('route_count', 0)} routes, and {summary.get('component_count', 0)} components read-only.", "confidence": _as_dict(memory_layers.get("semantic_memory")).get("confidence", "medium")},
        {"type": "episodic_memory", "summary": f"Evidence Librarian indexed {evidence_library.get('zip_count', counts['evidence'])} result/fail/context ZIPs for historical recall.", "confidence": _as_dict(memory_layers.get("episodic_memory")).get("confidence", "medium")},
        {"type": "procedural_memory", "summary": f"{protocols[0]['label']} ranked first; procedural memory keeps Mesh, gates, evidence, rollback, and no-fake-green rules active.", "confidence": _as_dict(memory_layers.get("procedural_memory")).get("confidence", "high")},
        {"type": "working_memory", "summary": f"Active interpretation is {interpretation.get('intent')} / {interpretation.get('area')} / {interpretation.get('lens')}.", "confidence": "high"},
        {"type": "operational_memory", "summary": f"Delta scanner available={delta.get('available', False)} with {delta.get('changed_count_sampled', 0)} changed and {delta.get('added_count_sampled', 0)} added sampled files.", "confidence": _as_dict(memory_layers.get("operational_memory")).get("confidence", "medium")},
        {"type": "visual_memory", "summary": f"Layer Investigator sampled {summary.get('css_count', 0)} CSS files across surfaces without adding visual mutations.", "confidence": _as_dict(memory_layers.get("visual_memory")).get("confidence", "medium")},
        {"type": "governance_memory", "summary": f"Authority memory manual_found={authority_memory.get('manual_found', False)} readset_found={authority_memory.get('readset_found', False)}; no DB writes, no .env reads, no deploy, no git push.", "confidence": _as_dict(memory_layers.get("governance_memory")).get("confidence", "medium")},
    ]



def _query_text_for_render(base: dict[str, Any], interpretation: dict[str, Any]) -> str:
    parts = [
        _as_str(base.get("_prismo_query") or base.get("query") or base.get("message") or base.get("direct_answer")),
        _as_str(interpretation.get("intent")),
        _as_str(interpretation.get("area")),
        _as_str(interpretation.get("lens")),
    ]
    return " ".join(part.lower() for part in parts if part)


def _pick_existing(blocks: list[dict[str, Any]], types: list[str]) -> str | None:
    available = {block.get("type") for block in blocks}
    for block_type in types:
        if block_type in available:
            return block_type
    return None


def _preferred_visual_type(query_text: str, interpretation: dict[str, Any], blocks: list[dict[str, Any]]) -> str | None:
    intent = _as_str(interpretation.get("intent")).lower()
    area = _as_str(interpretation.get("area")).lower()
    lens = _as_str(interpretation.get("lens")).lower()
    text = query_text.lower()
    if any(word in text for word in ["ruta", "route", "page", "layout", "endpoint"]):
        return _pick_existing(blocks, ["route_map", "chart_spec", "surface_matrix", "runtime_map"])
    if any(word in text for word in ["css", "layer", "selector", "z-index", "visual", "capa"]):
        return _pick_existing(blocks, ["layer_map", "chart_spec", "table_view", "surface_matrix"])
    if any(word in text for word in ["gráfic", "grafic", "chart", "métrica", "metrica", "número", "numero", "score", "porcentaje", "conteo", "cuánt", "cuant"]):
        return _pick_existing(blocks, ["chart_spec", "surface_matrix", "runtime_map", "impact_map"])
    if any(word in text for word in ["graph", "grafo", "flujo", "conecta", "depend", "mapa", "apps", "app live", "tiempo real", "runtime", "superficie"]) or lens == "runtime_state":
        return _pick_existing(blocks, ["chart_spec", "surface_matrix", "runtime_map", "impact_map", "flow_diagram"])
    if any(word in text for word in ["compar", "diff", "versus", " vs "]) or intent == "compare":
        return _pick_existing(blocks, ["diff_view", "chart_spec", "surface_matrix", "comparison_board"])
    if any(word in text for word in ["timeline", "línea", "linea", "cambió", "cambio", "histórico", "historico", "evoluci", "delta", "desde"]):
        return _pick_existing(blocks, ["timeline", "chart_spec"])
    if any(word in text for word in ["riesgo", "risk", "bloque", "blocker"]) or intent == "audit":
        return _pick_existing(blocks, ["risk_matrix", "chart_spec", "checklist"])
    if any(word in text for word in ["autoridad", "govern", "gobern", "canon", "preceden"]) or area == "governance":
        return _pick_existing(blocks, ["authority_map", "risk_matrix", "authority_strip"])
    if any(word in text for word in ["evidencia", "evidence", "vault", "log", "zip", "result", "fail"]):
        return _pick_existing(blocks, ["evidence_board", "chart_spec", "timeline", "evidence_cards", "context_pack_explorer"])
    if any(word in text for word in ["paso", "siguiente", "accion", "acción", "check", "terminar", "pendiente"]) or intent in {"recommend", "prepare_action"}:
        return _pick_existing(blocks, ["checklist", "chart_spec", "surface_matrix", "next_best_action", "protocol_ladder"])
    return _pick_existing(blocks, ["chart_spec", "surface_matrix", "route_map", "runtime_map", "flow_diagram", "checklist", "risk_matrix"])


def _shape_theater_blocks(base: dict[str, Any], interpretation: dict[str, Any], blocks: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str | None]:
    hidden = {"hero_response", "executive_brief", "next_best_action", "protocol_ladder", "procedural_steps", "technical_drawer", "action_bar", "feedback_dock", "memory_trace", "insight_chips", "authority_strip"}
    visual = [block for block in blocks if block.get("type") not in hidden]
    preferred = _preferred_visual_type(_query_text_for_render(base, interpretation), interpretation, visual)
    selected: list[dict[str, Any]] = []

    def take(predicate) -> None:
        if len(selected) >= 8:
            return
        for block in visual:
            if predicate(block) and not any(item.get("id") == block.get("id") for item in selected):
                selected.append(block)
                return

    if preferred:
        take(lambda block: block.get("type") == preferred)
    take(lambda block: block.get("type") in {"chart_spec", "surface_matrix", "route_map", "layer_map", "runtime_map", "impact_map", "flow_diagram", "diff_view", "timeline", "risk_matrix", "checklist", "evidence_board", "authority_map", "table_view"})
    take(lambda block: block.get("type") in {"next_best_action", "protocol_ladder", "executive_brief"})
    for block in visual:
        if len(selected) >= 8:
            break
        if not any(item.get("id") == block.get("id") for item in selected):
            selected.append(block)
    if not selected and blocks:
        selected = blocks[:1]
    shaped: list[dict[str, Any]] = []
    for index, block in enumerate(selected[:8]):
        item = dict(block)
        item["layout"] = "full" if index == 0 else item.get("layout", "half" if index < 3 else "third")
        item["visual_role"] = "primary" if index == 0 else "secondary"
        shaped.append(item)
    suppressed = [block for block in blocks if not any(item.get("id") == block.get("id") for item in shaped)]
    primary_type = shaped[0].get("type") if shaped else None
    return shaped, suppressed, primary_type



# PRISMO_FINAL_VISUAL_STAGE_BEGIN
def _clamp_answer_text(text: str, overflow_chars: int = 24000, overflow_lines: int = 320) -> str:
    # Nombre histórico conservado por compatibilidad: esto ya no mutila la respuesta a 5 líneas.
    # Sólo protege la UI contra salidas absurdamente enormes.
    cleaned = _as_str(text).replace("\r\n", "\n").strip()
    if not cleaned:
        cleaned = "PRISMO leyó el contexto disponible en modo read-only y preparó una respuesta trazable."
    cleaned = re.sub(r"\n{4,}", "\n\n\n", cleaned)
    lines = cleaned.splitlines()
    value = "\n".join(lines[:overflow_lines]).strip() if len(lines) > overflow_lines else cleaned
    if len(value) > overflow_chars:
        value = value[: max(0, overflow_chars - 72)].rstrip() + "\n\n…[respuesta abreviada sólo por protección anti-desborde de UI]"
    return value


def _visual_data_from_app_live(app_live: dict[str, Any], evidence: list[dict[str, Any]], risk: dict[str, Any]) -> dict[str, Any]:
    app_live = _as_dict(app_live or {})
    apps = [_as_dict(app) for app in _as_list(app_live.get("apps")) if _as_dict(app).get("exists", True)]
    surfaces: list[dict[str, Any]] = []
    route_nodes: list[dict[str, Any]] = []
    layer_rows: list[dict[str, Any]] = []
    for app in apps:
        surface_id = _as_str(app.get("id") or app.get("surface") or app.get("label") or "surface")
        label = _as_str(app.get("label") or app.get("id") or "Surface")
        surfaces.append({
            "id": surface_id,
            "label": label,
            "files": int(app.get("file_count") or 0),
            "routes": int(app.get("route_count") or 0),
            "components": int(app.get("component_count") or 0),
            "css": int(app.get("css_count") or 0),
            "docs": int(app.get("doc_count") or 0),
        })
        for route in _as_list(app.get("routes_sample"))[:16]:
            route = _as_dict(route)
            route_nodes.append({
                "id": _as_str(route.get("route") or route.get("rel") or "route"),
                "label": _as_str(route.get("route") or route.get("rel") or "route"),
                "surface": label,
                "status": "route",
                "summary": _as_str(route.get("rel") or ""),
            })
        for item in _as_list(app.get("layer_signals"))[:18]:
            item = _as_dict(item)
            layer_rows.append({
                "surface": label,
                "file": _as_str(item.get("file") or ""),
                "selector": _as_str(item.get("selector") or "")[:140],
                "z_index": ", ".join([_as_str(x) for x in _as_list(item.get("z_index"))]) or "",
                "important": int(item.get("important_count") or 0),
                "backdrop": bool(item.get("backdrop_filter")),
            })
    evidence_library = _as_dict(app_live.get("evidence_library"))
    delta = _as_dict(app_live.get("delta_scanner"))
    summary = _as_dict(app_live.get("summary"))
    memory_layers = _as_dict(app_live.get("memory_layers"))
    evidence_items = evidence if evidence else []
    visual_data = {
        "surface_metrics": surfaces,
        "route_nodes": route_nodes[:64],
        "layer_rows": layer_rows[:64],
        "summary": {
            "app_count": int(summary.get("app_count") or len(surfaces)),
            "file_count": int(summary.get("file_count") or sum(item["files"] for item in surfaces)),
            "route_count": int(summary.get("route_count") or sum(item["routes"] for item in surfaces)),
            "component_count": int(summary.get("component_count") or sum(item["components"] for item in surfaces)),
            "css_count": int(summary.get("css_count") or sum(item["css"] for item in surfaces)),
            "evidence_zip_count": int(summary.get("evidence_zip_count") or evidence_library.get("zip_count") or 0),
            "memory_layer_count": int(summary.get("memory_layer_count") or len(memory_layers)),
        },
        "evidence_metrics": {
            "zip_count": int(evidence_library.get("zip_count") or 0),
            "latest_result": bool(evidence_library.get("latest_result")),
            "latest_fail": bool(evidence_library.get("latest_fail")),
            "response_evidence_count": len(evidence_items),
        },
        "delta_metrics": {
            "available": bool(delta.get("available")),
            "changed": int(delta.get("changed_count_sampled") or 0),
            "added": int(delta.get("added_count_sampled") or 0),
            "changed_files_sample": _as_list(delta.get("changed_files_sample"))[:12],
            "added_files_sample": _as_list(delta.get("added_files_sample"))[:12],
        },
        "memory_layers": memory_layers,
        "risk": risk,
        "has_structured_data": bool(surfaces or evidence_library or delta or route_nodes or layer_rows),
    }
    if not visual_data["has_structured_data"]:
        visual_data["no_visual_reason"] = "insufficient_structured_data"
    return visual_data


def _surface_chart_block(visual_data: dict[str, Any], metric: str = "routes") -> dict[str, Any] | None:
    surfaces = [_as_dict(item) for item in _as_list(visual_data.get("surface_metrics")) if int(_as_dict(item).get(metric) or 0) > 0]
    if not surfaces:
        return None
    labels = [_as_str(item.get("label") or item.get("id")) for item in surfaces[:8]]
    route_data = [int(item.get("routes") or 0) for item in surfaces[:8]]
    component_data = [int(item.get("components") or 0) for item in surfaces[:8]]
    css_data = [int(item.get("css") or 0) for item in surfaces[:8]]
    return _block_contract(
        "visual_surface_metrics_chart",
        "chart_spec",
        "Visual Stage · Superficies del proyecto",
        "Comparación read-only de rutas, componentes y CSS por superficie.",
        12,
        {
            "chartType": "bar",
            "meta": {"title": "Superficies PRISMA por rutas, componentes y CSS", "description": "Comparación read-only de Project Brain; no modifica apps, procesos ni Prisma."},
            "labels": labels,
            "xAxis": {"data": labels, "label": "Superficie"},
            "series": [
                {"name": "Rutas", "label": "Rutas", "data": route_data},
                {"name": "Componentes", "label": "Componentes", "data": component_data},
                {"name": "CSS", "label": "CSS", "data": css_data},
            ],
            "rows": surfaces[:8],
            "footer": "Fuente: Project Brain read-only. No modifica apps ni procesos.",
        },
        "positive",
    )


def _surface_matrix_block(visual_data: dict[str, Any]) -> dict[str, Any] | None:
    rows = [_as_dict(item) for item in _as_list(visual_data.get("surface_metrics"))]
    if not rows:
        return None
    return _block_contract(
        "visual_surface_matrix",
        "surface_matrix",
        "Surface matrix",
        "Lectura tabular de archivos, rutas, componentes, CSS y docs por superficie.",
        24,
        {"rows": rows[:12], "columns": ["label", "files", "routes", "components", "css", "docs"]},
        "neutral",
    )


def _evidence_chart_block(visual_data: dict[str, Any]) -> dict[str, Any] | None:
    evidence = _as_dict(visual_data.get("evidence_metrics"))
    values = [int(evidence.get("zip_count") or 0), int(evidence.get("response_evidence_count") or 0), 1 if evidence.get("latest_result") else 0, 1 if evidence.get("latest_fail") else 0]
    if not any(values):
        return None
    return _block_contract(
        "visual_evidence_metrics_chart",
        "chart_spec",
        "Visual Stage · Evidencia disponible",
        "Conteo compacto de evidencias indexadas y señales result/fail recientes.",
        26,
        {
            "chartType": "bar",
            "labels": ["ZIPs", "Respuesta", "Latest result", "Latest fail"],
            "xAxis": {"data": ["ZIPs", "Respuesta", "Latest result", "Latest fail"], "label": "Tipo de evidencia"},
            "series": [{"name": "Conteo", "label": "Conteo", "data": values}],
            "footer": "Episodic memory / Evidence Librarian read-only.",
        },
        "neutral",
    )


def _delta_timeline_block(visual_data: dict[str, Any]) -> dict[str, Any] | None:
    delta = _as_dict(visual_data.get("delta_metrics"))
    if not delta.get("available"):
        return None
    events = [
        {"time": "Índice previo", "title": "Baseline disponible", "status": "ready", "summary": "PRISMO comparó contra el índice anterior guardado en Learning Store."},
        {"time": "Ahora", "title": f"{delta.get('changed', 0)} changed · {delta.get('added', 0)} added", "status": "read-only", "summary": "Delta scanner preparó muestra de cambios sin modificar el proyecto."},
    ]
    for item in _as_list(delta.get("changed_files_sample"))[:4]:
        item = _as_dict(item)
        events.append({"time": "sample", "title": _as_str(item.get("rel") or "archivo cambiado"), "status": "changed", "summary": _as_str(item.get("mtime") or "")})
    return _block_contract("visual_delta_timeline", "timeline", "Delta timeline", "Cambios detectados contra el índice anterior.", 28, {"events": events}, "neutral")


def _memory_table_block(visual_data: dict[str, Any]) -> dict[str, Any] | None:
    layers = _as_dict(visual_data.get("memory_layers"))
    if not layers:
        return None
    rows = []
    for key, value in layers.items():
        value = _as_dict(value)
        rows.append({"memory": _as_str(key).replace("_", " "), "confidence": _as_str(value.get("confidence") or "medium"), "purpose": _as_str(value.get("purpose") or "")})
    return _block_contract("visual_memory_table", "table_view", "Memorias chidas activas", "Capas de memoria usadas para entender PRISMA en modo read-only.", 32, {"rows": rows[:10], "columns": ["memory", "confidence", "purpose"]}, "neutral")



def _route_map_block(visual_data: dict[str, Any]) -> dict[str, Any] | None:
    nodes = [_as_dict(item) for item in _as_list(visual_data.get("route_nodes"))]
    if not nodes:
        return None
    return _block_contract(
        "visual_route_map",
        "route_map",
        "Route map",
        "Rutas detectadas por Project Brain en modo read-only.",
        18,
        {"nodes": nodes[:32]},
        "positive",
    )


def _layer_map_block(visual_data: dict[str, Any]) -> dict[str, Any] | None:
    rows = [_as_dict(item) for item in _as_list(visual_data.get("layer_rows"))]
    if not rows:
        return None
    return _block_contract(
        "visual_layer_map",
        "table_view",
        "Layer investigator",
        "Selectores, z-index, backdrop y deuda visual muestreados sin modificar CSS.",
        22,
        {"rows": rows[:20], "columns": ["surface", "file", "selector", "z_index", "important", "backdrop"]},
        "neutral",
    )


def _brain100_query_profile(query: str, interpretation: dict[str, Any]) -> dict[str, Any]:
    text = (query or "").lower()
    categories = {
        "surfaces": ["app", "apps", "superficie", "surface", "tablet", "pc", "mobile", "chart"],
        "routes": ["ruta", "route", "page", "layout", "endpoint"],
        "layers": ["css", "layer", "selector", "z-index", "capa", "visual"],
        "evidence": ["evidencia", "evidence", "zip", "fail", "result", "log"],
        "delta": ["cambio", "cambió", "delta", "desde", "ayer", "timeline", "histórico", "historico"],
        "memory": ["memoria", "memory", "procedural", "semant", "episod", "aprendiz"],
        "risk": ["riesgo", "risk", "bloque", "blocker", "gate", "gobern", "autoridad"],
        "build": ["terminar", "desarroll", "útil", "util", "mejora", "arregl", "funcion"],
        "graph": ["grafo", "graph", "mapa", "depend", "conecta", "flujo"],
        "chart": ["graf", "chart", "métrica", "metrica", "número", "numero", "conteo", "cuánt", "cuant"],
    }
    scores = {name: sum(1 for word in words if word in text) for name, words in categories.items()}
    intent = max(scores, key=lambda key: scores[key]) if any(scores.values()) else _as_str(interpretation.get("intent") or "general")
    return {"scores": scores, "primary": intent, "matched": [key for key, value in scores.items() if value], "raw_query": query}


def _brain100_dependency_graph_block(visual_data: dict[str, Any]) -> dict[str, Any] | None:
    surfaces = [_as_dict(item) for item in _as_list(visual_data.get("surface_metrics"))]
    if not surfaces:
        return None
    nodes = [{"id": "project_brain", "label": "Project Brain", "status": "read-only", "summary": "Índice vivo local"}]
    for item in surfaces[:10]:
        nodes.append({
            "id": _as_str(item.get("id") or item.get("label")),
            "label": _as_str(item.get("label") or item.get("id")),
            "status": f"{int(item.get('routes') or 0)} rutas",
            "summary": f"{int(item.get('files') or 0)} files · {int(item.get('components') or 0)} comps · {int(item.get('css') or 0)} CSS",
        })
    return _block_contract("brain100_dependency_graph", "dependency_graph", "Mapa de conocimiento", "Cómo PRISMO conecta Project Brain con superficies leídas en modo read-only.", 16, {"nodes": nodes}, "positive")


def _brain100_capability_block(profile: dict[str, Any], visual_data: dict[str, Any]) -> dict[str, Any]:
    summary = _as_dict(visual_data.get("summary"))
    evidence = _as_dict(visual_data.get("evidence_metrics"))
    delta = _as_dict(visual_data.get("delta_metrics"))
    layers = _as_dict(visual_data.get("memory_layers"))
    items = [
        {"label": "Project Brain activo", "done": bool(summary.get("file_count")), "status": f"{summary.get('file_count', 0)} files / {summary.get('route_count', 0)} rutas"},
        {"label": "Visual Stage con datos", "done": bool(visual_data.get("has_structured_data")), "status": profile.get("primary", "general")},
        {"label": "Evidence Librarian", "done": bool(evidence.get("zip_count")), "status": f"{evidence.get('zip_count', 0)} ZIPs"},
        {"label": "Delta Scanner", "done": bool(delta.get("available")), "status": f"{delta.get('changed', 0)} changed / {delta.get('added', 0)} added"},
        {"label": "Memorias chidas", "done": bool(layers), "status": f"{len(layers)} capas"},
        {"label": "Read-only contract", "done": True, "status": "sin mutación"},
    ]
    return _block_contract("brain100_capability_checklist", "checklist", "Inteligencia activa", "Capacidades que PRISMO usó o puede usar para entender PRISMA.", 30, {"items": items}, "positive")


def _brain100_reasoning_table_block(profile: dict[str, Any], visual_data: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for key, value in sorted(_as_dict(profile.get("scores")).items(), key=lambda item: item[1], reverse=True):
        rows.append({"signal": key, "score": value, "used": "yes" if value else "available"})
    rows.append({"signal": "structured_data", "score": 1 if visual_data.get("has_structured_data") else 0, "used": "visual gate"})
    rows.append({"signal": "primary", "score": profile.get("primary", "general"), "used": "router"})
    return _block_contract("brain100_reasoning_router", "table_view", "Router de inteligencia", "Por qué PRISMO eligió esas formas de respuesta.", 34, {"rows": rows[:14], "columns": ["signal", "score", "used"]}, "neutral")



def _brainfinal_development_readiness_block(profile: dict[str, Any], visual_data: dict[str, Any]) -> dict[str, Any]:
    summary = _as_dict(visual_data.get("summary"))
    evidence = _as_dict(visual_data.get("evidence_metrics"))
    delta = _as_dict(visual_data.get("delta_metrics"))
    items = [
        {"label": "Puede orientar desarrollo read-only", "done": bool(summary.get("file_count")), "status": f"{summary.get('file_count', 0)} files vistos"},
        {"label": "Tiene mapa de rutas", "done": bool(summary.get("route_count")), "status": f"{summary.get('route_count', 0)} rutas"},
        {"label": "Tiene mapa de componentes", "done": bool(summary.get("component_count")), "status": f"{summary.get('component_count', 0)} componentes"},
        {"label": "Tiene mapa visual/CSS", "done": bool(summary.get("css_count")), "status": f"{summary.get('css_count', 0)} CSS"},
        {"label": "Tiene memoria episódica", "done": bool(evidence.get("zip_count")), "status": f"{evidence.get('zip_count', 0)} ZIPs"},
        {"label": "Puede comparar deltas", "done": bool(delta.get("available")), "status": f"{delta.get('changed', 0)} changed / {delta.get('added', 0)} added"},
    ]
    return _block_contract("brainfinal_development_readiness", "checklist", "Readiness para desarrollar PRISMA", "Qué tan preparado está PRISMO para ayudarte sin tocar el proyecto.", 14, {"items": items}, "positive")


def _brainfinal_risk_matrix_block(profile: dict[str, Any], visual_data: dict[str, Any]) -> dict[str, Any]:
    summary = _as_dict(visual_data.get("summary"))
    evidence = _as_dict(visual_data.get("evidence_metrics"))
    delta = _as_dict(visual_data.get("delta_metrics"))
    layers = _as_dict(visual_data.get("memory_layers"))
    items = [
        {"risk": "Contexto insuficiente", "level": "low" if summary.get("file_count") else "medium", "summary": f"{summary.get('file_count', 0)} archivos indexados.", "mitigation": "Refrescar Project Brain antes de decidir."},
        {"risk": "Evidencia vieja o ausente", "level": "low" if evidence.get("zip_count") else "medium", "summary": f"{evidence.get('zip_count', 0)} ZIPs en Evidence Librarian.", "mitigation": "Usar result/fail ZIPs recientes como autoridad."},
        {"risk": "Cambio no comparado", "level": "low" if delta.get("available") else "medium", "summary": "Delta disponible." if delta.get("available") else "Aún sin baseline comparativo.", "mitigation": "Generar otro índice tras cambios para comparar deriva."},
        {"risk": "Capas visuales complejas", "level": "medium" if summary.get("css_count", 0) > 80 else "low", "summary": f"{summary.get('css_count', 0)} CSS detectados.", "mitigation": "Usar Layer Investigator antes de mover UI."},
        {"risk": "Memoria no aplicada", "level": "low" if layers else "medium", "summary": f"{len(layers)} capas de memoria disponibles.", "mitigation": "Consultar semántica/procedural/episódica según consulta."},
    ]
    return _block_contract("brainfinal_risk_matrix", "risk_matrix", "Riesgos de interpretación", "Riesgos read-only antes de usar una conclusión para desarrollo.", 20, {"items": items}, "neutral")


def _brain100_answer_text(base: dict[str, Any], profile: dict[str, Any], visual_data: dict[str, Any], primary_type: str | None) -> str:
    summary = _as_dict(visual_data.get("summary"))
    surfaces = [_as_dict(item) for item in _as_list(visual_data.get("surface_metrics"))]
    top_routes = sorted(surfaces, key=lambda item: int(item.get("routes") or 0), reverse=True)[:4]
    top_files = sorted(surfaces, key=lambda item: int(item.get("files") or 0), reverse=True)[:4]
    top_css = sorted(surfaces, key=lambda item: int(item.get("css") or 0), reverse=True)[:4]
    evidence = _as_dict(visual_data.get("evidence_metrics"))
    delta = _as_dict(visual_data.get("delta_metrics"))
    layers = _as_dict(visual_data.get("memory_layers"))
    matched = ", ".join(_as_list(profile.get("matched"))[:8]) or "general"

    lines = [
        f"Leí PRISMA en modo read-only y detecté {summary.get('app_count', len(surfaces))} superficies, {summary.get('file_count', 0)} archivos, {summary.get('route_count', 0)} rutas, {summary.get('component_count', 0)} componentes, {summary.get('css_count', 0)} CSS y {summary.get('memory_layer_count', len(layers))} capas de memoria.",
        f"Interpreté tu consulta como `{profile.get('primary', 'general')}` con señales `{matched}`. Por eso el visual principal es `{primary_type or 'visual automático'}` y dejé matrices, timeline, memoria, riesgo o grafo como apoyo cuando hay datos.",
    ]
    if top_files:
        lines.append("Superficies con más archivos: " + "; ".join(f"{item.get('label')}: {item.get('files')}" for item in top_files) + ".")
    if top_routes:
        lines.append("Superficies con más rutas: " + "; ".join(f"{item.get('label')}: {item.get('routes')}" for item in top_routes) + ".")
    if top_css:
        lines.append("Mayor carga CSS/visual detectada: " + "; ".join(f"{item.get('label')}: {item.get('css')}" for item in top_css) + ". Esto no implica error, pero sí indica dónde conviene usar Layer Investigator antes de tocar UI.")
    if evidence.get("zip_count"):
        lines.append(f"Evidence Librarian trae {evidence.get('zip_count')} ZIPs indexados; latest_result={bool(evidence.get('latest_result'))}, latest_fail={bool(evidence.get('latest_fail'))}. Esa memoria episódica sirve para explicar fallos pasados sin inventar causa raíz.")
    else:
        lines.append("Evidence Librarian no reporta ZIPs suficientes en esta lectura; si preguntas por fallos o regresiones, la confianza debe bajar hasta refrescar evidencia.")
    if delta.get("available"):
        lines.append(f"Delta Scanner comparó contra índice previo: {delta.get('changed', 0)} changed y {delta.get('added', 0)} added. Esa señal ayuda a responder qué cambió sin hacer git write ni tocar procesos.")
    else:
        lines.append("Delta Scanner todavía está en modo baseline o primer índice; puede entender el estado actual, pero no afirmar cambios históricos fuertes sin otro índice posterior.")
    if layers:
        lines.append("Memorias activas: " + "; ".join(f"{k.replace('_', ' ')}={_as_dict(v).get('confidence', 'medium')}" for k, v in list(layers.items())[:8]) + ".")
    lines.append("Para terminar de desarrollar PRISMA, úsalo como cerebro observador: pregúntale por superficies, rutas, CSS/capas, evidencia reciente, riesgos, deudas o qué falta. En este modo no modifica apps; observa, entiende, memoriza y visualiza con evidencia.")
    return "\n\n".join(lines)


def _build_visual_stage_blocks(base: dict[str, Any], interpretation: dict[str, Any], visual_data: dict[str, Any]) -> list[dict[str, Any]]:
    query = _query_text_for_render(base, interpretation)
    profile = _brain100_query_profile(query, interpretation)
    blocks: list[dict[str, Any]] = []
    wants = set(_as_list(profile.get("matched")))
    chart = _surface_chart_block(visual_data)
    matrix = _surface_matrix_block(visual_data)
    route_map = _route_map_block(visual_data)
    layer_map = _layer_map_block(visual_data)
    evidence_chart = _evidence_chart_block(visual_data)
    delta_timeline = _delta_timeline_block(visual_data)
    memory_table = _memory_table_block(visual_data)
    dependency = _brain100_dependency_graph_block(visual_data)
    capability = _brain100_capability_block(profile, visual_data)
    reasoning = _brain100_reasoning_table_block(profile, visual_data)
    readiness = _brainfinal_development_readiness_block(profile, visual_data)
    risk_matrix = _brainfinal_risk_matrix_block(profile, visual_data)

    def add(block: dict[str, Any] | None) -> None:
        if block and not any(item.get("id") == block.get("id") for item in blocks):
            blocks.append(block)

    if "routes" in wants:
        add(route_map); add(chart); add(matrix)
    elif "layers" in wants:
        add(layer_map); add(chart); add(matrix)
    elif "evidence" in wants:
        add(evidence_chart); add(delta_timeline); add(chart)
    elif "delta" in wants:
        add(delta_timeline); add(evidence_chart); add(chart)
    elif "memory" in wants:
        add(memory_table); add(capability); add(reasoning)
    elif "graph" in wants:
        add(dependency); add(route_map); add(chart)
    elif "risk" in wants:
        add(risk_matrix); add(reasoning); add(evidence_chart); add(delta_timeline)
    else:
        add(chart); add(matrix); add(dependency)

    for optional in [matrix, route_map, layer_map, evidence_chart, delta_timeline, memory_table, risk_matrix, readiness, capability, reasoning, dependency]:
        add(optional)
    if not blocks and visual_data.get("no_visual_reason"):
        blocks.append(_block_contract("visual_stage_empty", "direct_answer_card", "Sin visual estructurado", f"No visual: {visual_data.get('no_visual_reason')}", 12, {"answer": f"No visual: {visual_data.get('no_visual_reason')}"}, "neutral"))
    return blocks[:12]


def _answer_channel_from_visual_data(base: dict[str, Any], visual_data: dict[str, Any], primary_type: str | None) -> dict[str, Any]:
    query = _query_text_for_render(base, _as_dict(base.get("interpretation") or {}))
    profile = _brain100_query_profile(query, _as_dict(base.get("interpretation") or {}))
    direct = _as_str(base.get("direct_answer"))
    surfaces = _as_list(visual_data.get("surface_metrics"))
    if surfaces:
        text = _brain100_answer_text(base, profile, visual_data, primary_type)
        full = text
        if direct and len(direct) > 120 and "PRISMO" not in direct[:40]:
            full = direct + "\n\n" + text
    else:
        text = direct or "PRISMO respondió con el contexto disponible, sin mutar el proyecto."
        full = text
    return {
        "contract": "prismo.answer_channel.brainfinal.v2",
        "main_text": _clamp_answer_text(text),
        "short_text": _clamp_answer_text(text),
        "full_text": _clamp_answer_text(full, overflow_chars=32000, overflow_lines=420),
        "overflow_guard": "no_artificial_answer_cap_reasonable_ui_guard",
        "visual_stage_required": bool(visual_data.get("has_structured_data")),
        "primary_visual_type": primary_type,
        "no_visual_reason": visual_data.get("no_visual_reason", ""),
        "query_profile": profile,
    }
# PRISMO_FINAL_VISUAL_STAGE_END

def _app_live_runtime_block(app_live: dict[str, Any]) -> dict[str, Any] | None:
    if not app_live or not app_live.get("ok"):
        return None
    apps = _as_list(app_live.get("apps"))
    summary = _as_dict(app_live.get("summary"))
    evidence = _as_dict(app_live.get("evidence_library"))
    delta = _as_dict(app_live.get("delta_scanner"))
    signals = [
        {"label": "Project Brain", "status": f"{_as_str(summary.get('file_count') or 0)} files · {_as_str(summary.get('route_count') or 0)} rutas · {_as_str(summary.get('memory_layer_count') or 0)} memorias"},
        {"label": "Evidence Librarian", "status": f"{_as_str(evidence.get('zip_count') or 0)} ZIPs indexados · latest_fail={bool(evidence.get('latest_fail'))}"},
        {"label": "Delta Scanner", "status": f"available={bool(delta.get('available'))} · changed={_as_str(delta.get('changed_count_sampled') or 0)} · added={_as_str(delta.get('added_count_sampled') or 0)}"},
    ]
    for app in apps[:6]:
        app = _as_dict(app)
        signals.append({
            "label": f"{_as_str(app.get('label') or app.get('id'))}: {_as_str(app.get('route_count') or 0)} rutas",
            "status": f"{_as_str(app.get('file_count') or 0)} files · {_as_str(app.get('component_count') or 0)} comps · {_as_str(app.get('css_count') or 0)} css",
        })
    return _block_contract(
        "app_live_context",
        "runtime_map",
        "Project Brain · App Live Context",
        "PRISMO indexed project apps, evidence ZIPs, memory layers, deltas, authority and CSS layers read-only before answering.",
        22,
        {"signals": signals, "cache": app_live.get("cache_path"), "generated_at": app_live.get("generated_at"), "memory_layers": app_live.get("memory_layers")},
        "positive",
    )

def _build_theater_blocks(base: dict[str, Any], interpretation: dict[str, Any], snapshot: dict[str, Any], memory_used: list[dict[str, Any]], protocols: list[dict[str, Any]], app_live: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    evidence = _evidence_summary([_as_dict(item) for item in _as_list(base.get("evidence"))])
    risk = _as_dict(base.get("risk"))
    authority = _as_dict(base.get("authority"))
    direct_answer = _as_str(base.get("direct_answer"))
    next_step = _as_str(base.get("safe_next_step") or "Review evidence and run the narrowest verifier.")
    chains = ["question", "interpretation", "protocol", "evidence", "result", "feedback"]
    app_live_block = _app_live_runtime_block(_as_dict(app_live or {}))
    visual_data = _visual_data_from_app_live(_as_dict(app_live or {}), evidence, risk)
    visual_stage_blocks = _build_visual_stage_blocks(base, interpretation, visual_data)
    blocks = [
        _block_contract("hero_response", "hero_response", "PRISMO response", direct_answer, 10, {"answer": direct_answer, "confidence": interpretation.get("confidence"), "interpretation": interpretation}, "positive"),
        *visual_stage_blocks,
        _block_contract("executive_brief", "executive_brief", "Executive brief", "PRISMO synthesized the current signal into operational priority, authority, and next action.", 20, {"sections": [{"title": "Priority", "items": [direct_answer]}, {"title": "Authority", "items": [_as_str(authority.get("winning_source") or "PRISMO runtime")]}, {"title": "Next", "items": [next_step]}]}),
        _block_contract("next_best_action", "next_best_action", "Next best action", next_step, 30, {"action": next_step, "impact": risk.get("level", "contextual"), "review_required": True}, "positive"),
        _block_contract("protocol_ladder", "protocol_ladder", "Protocol ladder", "Procedural memory ranked the safest protocol path for this answer.", 40, {"protocols": protocols, "ranking_basis": ["semantic match", "area/lens compatibility", "recent evidence", "governance constraints", "feedback statistics when available"]}),
        _block_contract("procedural_steps", "procedural_steps", "Procedural memory", "Recommended path derived from procedural memory and governance.", 50, {"steps": [{"id": "read", "label": "Read current evidence", "status": "ready"}, {"id": "verify", "label": "Run narrow verifier", "status": "ready"}, {"id": "decide", "label": "Prepare governed action only if evidence supports it", "status": "guarded"}]}),
        _block_contract("evidence_board", "evidence_board", "Evidence board", "Evidence is summarized by source, freshness, confidence, and relevance.", 60, {"items": evidence}),
        _block_contract("risk_matrix", "risk_matrix", "Risk matrix", _as_str(risk.get("summary") or "Risk remains governed by read-only safety."), 70, {"items": [{"risk": _as_str(risk.get("summary") or "Operational uncertainty"), "level": _as_str(risk.get("level") or "medium"), "mitigation": next_step}]}),
        _block_contract("memory_trace", "memory_trace", "Memory trace", "Semantic, episodic, procedural, working, operational, visual, and governance memory informed this answer.", 80, {"items": memory_used}),
        _block_contract("authority_strip", "authority_strip", "Authority strip", _as_str(authority.get("notes") or "Authority resolved by PRISMO runtime."), 90, {"winning_source": authority.get("winning_source"), "precedence": _as_list(authority.get("precedence_applied"))}),
        _block_contract("insight_chips", "insight_chips", "Insight chips", "Key inferences remain editable and inspectable.", 100, {"chips": interpretation.get("chips", [])}),
        _block_contract("flow_diagram", "flow_diagram", "Response chain", "question -> interpretation -> protocol -> evidence -> result -> feedback", 110, {"nodes": [{"id": chain, "label": chain.replace("_", " ").title(), "status": "ready"} for chain in chains]}),
        _block_contract("technical_drawer", "technical_drawer", "Technical detail", "Full interpretation, render plan, memory, evidence, protocols, safety, and traces are available in the drawer.", 120, {"default_open": False}, collapsible=True),
        _block_contract("action_bar", "action_bar", "Action bar", "Review impact, prepare action, save reference, or open technical detail.", 130, {"actions": ["review_impact", "prepare_action", "save_reference", "open_technical_detail"]}),
        _block_contract("feedback_dock", "feedback_dock", "Feedback dock", "Feedback can update the safe adapter and influence later protocol ranking when persistence is available.", 140, {"states": ["pending", "helpful", "not_helpful", "saved_reference", "converted_to_protocol", "adjusted"]}),
    ]
    if app_live_block:
        app_live_block["priority"] = 34
        app_live_block["layout"] = "half"
        blocks.append(app_live_block)
    return blocks


def _build_render_plan(request_id: str, interpretation: dict[str, Any], blocks: list[dict[str, Any]], primary_block_type: str | None = None, suppressed_blocks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    suppressed_blocks = suppressed_blocks or []
    return {
        "id": f"{request_id}_auto_render_plan",
        "schema_version": "prismo.auto_render_plan.v1",
        "auto_render_ensemble": True,
        "selection": {
            "source": "render_plan",
            "user_selected_block": None,
            "primary_block_type": primary_block_type,
            "visible_block_count": len(blocks),
            "suppressed_block_count": len(suppressed_blocks),
            "forbidden_manual_selectors": ["scene", "format", "output_type", "checklist", "timeline", "risk_matrix", "evidence_board", "flow_diagram", "render_block"],
        },
        "interpretation": interpretation,
        "suppressed_blocks": [
            {"id": block.get("id"), "type": block.get("type"), "title": block.get("title"), "reason": "kept in technical drawer to avoid visual duplication"}
            for block in suppressed_blocks
        ],
        "blocks": [
            {
                "id": block.get("id"),
                "type": block.get("type"),
                "title": block.get("title"),
                "priority": block.get("priority"),
                "status": block.get("status"),
                "tone": block.get("tone"),
                "collapsible": block.get("collapsible"),
            }
            for block in blocks
        ],
    }


def _response_memory_chain(payload: dict[str, Any], base: dict[str, Any], interpretation: dict[str, Any], protocols: list[dict[str, Any]], evidence: list[dict[str, Any]], render_plan: dict[str, Any]) -> dict[str, Any]:
    query = _collect_message(payload)
    return {
        "question": {
            "text": query,
            "context": _as_str(payload.get("context") or payload.get("contextText") or payload.get("evidenceText") or ""),
            "timestamp": _now(),
        },
        "interpretation": {
            "intent": interpretation.get("intent"),
            "area": interpretation.get("area"),
            "lens": interpretation.get("lens"),
            "confidence": interpretation.get("confidence"),
            "source": interpretation.get("source"),
            "rationale": interpretation.get("rationale"),
        },
        "protocol": {
            "selected_protocols": protocols,
            "ranking_basis": ["semantic match", "guidance compatibility", "evidence relevance", "procedural memory", "governance constraints"],
            "procedural_memory_used": [protocols[0]] if protocols else [],
        },
        "evidence": {
            "evidence_ids": [item.get("id") for item in evidence],
            "evidence_summary": evidence,
            "confidence": 0.78 if evidence else 0.42,
        },
        "result": {
            "hero_summary": _as_str(base.get("direct_answer")),
            "next_best_action": _as_str(base.get("safe_next_step")),
            "render_plan_id": render_plan.get("id"),
            "block_ids": [block.get("id") for block in _as_list(render_plan.get("blocks"))],
            "status": "answered" if base.get("status") == "success" else "recoverable_error" if base.get("status") in {"blocked", "error"} else "partial",
        },
        "feedback": {
            "state": "pending",
            "notes": "",
            "timestamp": "",
        },
    }



def _prismo_local_readonly_base_response(payload: dict[str, Any], public: bool = False, query: str | None = None) -> dict[str, Any]:
    """Fast local-first response for PRISMO Theater.

    The theater is a read-only project brain. It must stay useful even when the
    live provider is slow, missing, or unreachable. This helper intentionally
    avoids network providers and creates a safe local response that the visual
    hydrator can enrich with Project Brain, memories and evidence.
    """
    payload = _as_dict(payload)
    request_id = _request_id()
    mode = _mode(payload.get("mode"))
    message = query if query is not None else _collect_message(payload)
    evidence_raw = _collect_evidence(payload)
    evidence, evidence_events = sanitize_text(evidence_raw, max_chars=250000)
    context = build_context_packet(evidence)
    context.setdefault("safetyEvents", [])
    context["safetyEvents"].extend(evidence_events)
    warnings = ["PRISMO_LOCAL_FIRST_READONLY_THEATER"]
    if public:
        warnings.append("PUBLIC_REDACTED_READ_ONLY")
    response = make_demo_response(mode, message, context, request_id, warnings=warnings)
    response = _as_dict(response)
    response["ok"] = response.get("ok") is not False
    response["status"] = response.get("status") or "success"
    response["request_id"] = request_id
    response["mode"] = mode
    response["demo_mode"] = True
    response["read_only"] = True
    response["mutation_allowed"] = False
    response.setdefault("evidence", evidence_cards_from_context(context))
    response.setdefault("certainty_level", "CONFIRMADO_POR_INDICE_LOCAL")
    response.setdefault("authority", {
        "winning_source": "PRISMO_LOCAL_FIRST_READONLY_THEATER",
        "winning_source_type": "runtime_contract",
        "precedence_applied": ["current Project Brain", "Learning Store", "read-only contract"],
        "notes": "Respuesta local-first para evitar bloqueo por proveedor externo."
    })
    response.setdefault("risk", {
        "level": "low",
        "summary": "Modo local read-only; sin mutación.",
        "reasons": [],
        "mitigations": ["Usar Project Brain y evidencia local como fuente primaria."]
    })
    response.setdefault("safe_next_step", "Consultar el Visual Stage y Project Brain antes de cualquier plan externo.")
    response.setdefault("warnings", [])
    response["warnings"] = _as_list(response.get("warnings")) + warnings
    response.setdefault("errors", [])
    response["meta"] = _as_dict(response.get("meta"))
    response["meta"]["provider"] = "local_project_brain"
    response["meta"]["schema_version"] = "brainfinal_readonly_v2"
    response["meta"]["local_first"] = True
    return response


def prismo_theater_query_payload(payload: dict[str, Any], public: bool = False) -> dict[str, Any]:
    payload = _as_dict(payload)
    query = _collect_message(payload)
    base = _prismo_local_readonly_base_response(payload, public=public, query=query)
    base["_prismo_query"] = query
    if public:
        base.setdefault("technical_trace", {})
        base["technical_trace"] = {"adapter_path": "internal/py/prismo_ai_bridge.py::prismo_theater_query_payload", "public": True, "missing_sources": ["local_only_theater_query"]}
        return base

    interpretation = _infer_interpretation(payload, query, base)
    snapshot, missing_sources = _learning_snapshot(query)
    app_live: dict[str, Any] = {}
    if _prismo_app_live_context_payload is not None:
        try:
            app_live = _prismo_app_live_context_payload(query=query, public=False)
        except Exception as exc:  # noqa: BLE001 - live context must never block an answer.
            missing_sources.append(f"prismo_app_live_context:{type(exc).__name__}")
            app_live = {"ok": False, "error": type(exc).__name__}
    else:
        missing_sources.append("prismo_app_live_context:unavailable")
    protocols = _selected_protocols(snapshot, interpretation)
    memory_used = _memory_used(snapshot, interpretation, protocols, app_live=app_live)
    raw_blocks = _build_theater_blocks(base, interpretation, snapshot, memory_used, protocols, app_live=app_live)
    blocks, suppressed_blocks, primary_block_type = _shape_theater_blocks(base, interpretation, raw_blocks)
    render_plan = _build_render_plan(_as_str(base.get("request_id") or _request_id()), interpretation, blocks, primary_block_type=primary_block_type, suppressed_blocks=suppressed_blocks)
    evidence = _evidence_summary([_as_dict(item) for item in _as_list(base.get("evidence"))])
    visual_data = _visual_data_from_app_live(_as_dict(app_live or {}), evidence, _as_dict(base.get("risk")))
    answer_channel = _answer_channel_from_visual_data(base, visual_data, primary_block_type)
    chain = _response_memory_chain(payload, base, interpretation, protocols, evidence, render_plan)
    safety = {
        "read_only": True,
        "mutation_allowed": False,
        "db_writes": False,
        "env_reads": False,
        "deploy": False,
        "git_push": False,
        "raw_html": False,
        "browser_automation": False,
    }
    technical_trace = {
        "adapter_path": "internal/py/prismo_ai_bridge.py::prismo_theater_query_payload",
        "frontend_endpoint": "POST /api/prismo/theater/query",
        "legacy_query_adapter": "internal/py/prismo_ai_bridge.py::prismo_query_payload",
        "learning_sources": [
            "/api/prismo/learning/status",
            "/api/prismo/learning/evidence-index",
            "/api/prismo/learning/recommend-protocol",
            "/api/prismo/learning/insights",
            "/api/prismo/learning/feedback",
        ],
        "missing_sources": missing_sources,
        "app_live_context": app_live,
        "suppressed_render_blocks": [{"id": b.get("id"), "type": b.get("type"), "title": b.get("title")} for b in suppressed_blocks],
        "response_chain_order": RESPONSE_CHAIN,
    }
    theater = {
        **base,
        "ok": bool(base.get("ok", True)),
        "interpretation": interpretation,
        "hero": {
            "title": "PRISMO response",
            "summary": _as_str(base.get("direct_answer")),
            "next_best_action": _as_str(base.get("safe_next_step")),
        },
        "answer_channel": answer_channel,
        "visual_data": visual_data,
        "visual_stage": {"contract": "prismo.visual_stage.v2", "primary_block_type": primary_block_type, "required": bool(visual_data.get("has_structured_data")), "no_visual_reason": visual_data.get("no_visual_reason", "")},
        "render_plan": render_plan,
        "blocks": blocks,
        "render_blocks": blocks,
        "actions": [
            {"id": "review_impact", "label": "Review impact"},
            {"id": "prepare_action", "label": "Prepare action"},
            {"id": "save_reference", "label": "Save reference"},
            {"id": "open_technical_detail", "label": "Open technical detail"},
            {"id": "adjust_recommendation", "label": "Adjust recommendation"},
        ],
        "evidence": evidence,
        "memory_used": memory_used,
        "response_memory_chain": chain,
        "technical_trace": technical_trace,
        "safety": safety,
        "feedback": {"state": "pending", "adapter": "/api/prismo/learning/feedback", "long_term_memory_claimed": False},
    }
    theater["direct_answer"] = answer_channel.get("short_text") or _as_str(theater.get("direct_answer"))
    theater["meta"] = _as_dict(theater.get("meta"))
    theater["meta"]["theater_adapter"] = "prismo_theater_query_payload"
    theater["meta"]["render_block_count"] = len(blocks)
    theater["meta"]["suppressed_render_block_count"] = len(suppressed_blocks)
    return theater


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
        "safe_next_step": "Reintentar la consulta o revisar el reporte PRISMO local.",
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
