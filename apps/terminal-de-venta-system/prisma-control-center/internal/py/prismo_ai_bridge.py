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


def _memory_used(snapshot: dict[str, Any], interpretation: dict[str, Any], protocols: list[dict[str, Any]]) -> list[dict[str, Any]]:
    status = _as_dict(snapshot.get("status"))
    insights = _as_dict(snapshot.get("insights"))
    counts = {
        "evidence": status.get("evidence_count", 0),
        "patterns": status.get("pattern_count", len(_as_list(insights.get("patterns")))),
        "protocols": len(protocols),
    }
    return [
        {"type": "semantic_memory", "summary": "PRISMO vocabulary, surfaces, and render block meanings shaped the normalized query.", "confidence": "high"},
        {"type": "episodic_memory", "summary": f"Evidence Vault supplied {counts['evidence']} indexed evidence records when available.", "confidence": "medium"},
        {"type": "procedural_memory", "summary": f"{protocols[0]['label']} ranked first because similar requests benefit from guided verification before action.", "confidence": "high"},
        {"type": "working_memory", "summary": f"Active interpretation is {interpretation.get('intent')} / {interpretation.get('area')} / {interpretation.get('lens')}.", "confidence": "high"},
        {"type": "operational_memory", "summary": f"Runtime snapshot reports {counts['patterns']} patterns and {counts['protocols']} protocol candidates.", "confidence": "medium"},
        {"type": "visual_memory", "summary": "Cloudglass/Refrigerant transparency, z-index, motion, and no-opacity-downgrade rules remain active.", "confidence": "high"},
        {"type": "governance_memory", "summary": "No DB writes, no .env reads, no deploy, no git push, no raw HTML/script execution.", "confidence": "high"},
    ]


def _build_theater_blocks(base: dict[str, Any], interpretation: dict[str, Any], snapshot: dict[str, Any], memory_used: list[dict[str, Any]], protocols: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence = _evidence_summary([_as_dict(item) for item in _as_list(base.get("evidence"))])
    risk = _as_dict(base.get("risk"))
    authority = _as_dict(base.get("authority"))
    direct_answer = _as_str(base.get("direct_answer"))
    next_step = _as_str(base.get("safe_next_step") or "Review evidence and run the narrowest verifier.")
    chains = ["question", "interpretation", "protocol", "evidence", "result", "feedback"]
    return [
        _block_contract("hero_response", "hero_response", "PRISMO response", direct_answer, 10, {"answer": direct_answer, "confidence": interpretation.get("confidence"), "interpretation": interpretation}, "positive"),
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


def _build_render_plan(request_id: str, interpretation: dict[str, Any], blocks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": f"{request_id}_auto_render_plan",
        "schema_version": "prismo.auto_render_plan.v1",
        "auto_render_ensemble": True,
        "selection": {
            "source": "render_plan",
            "user_selected_block": None,
            "forbidden_manual_selectors": ["scene", "format", "output_type", "checklist", "timeline", "risk_matrix", "evidence_board", "flow_diagram", "render_block"],
        },
        "interpretation": interpretation,
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


def prismo_theater_query_payload(payload: dict[str, Any], public: bool = False) -> dict[str, Any]:
    payload = _as_dict(payload)
    base = prismo_query_payload(payload, public=public)
    query = _collect_message(payload)
    if public:
        base.setdefault("technical_trace", {})
        base["technical_trace"] = {"adapter_path": "internal/py/prismo_ai_bridge.py::prismo_theater_query_payload", "public": True, "missing_sources": ["local_only_theater_query"]}
        return base

    interpretation = _infer_interpretation(payload, query, base)
    snapshot, missing_sources = _learning_snapshot(query)
    protocols = _selected_protocols(snapshot, interpretation)
    memory_used = _memory_used(snapshot, interpretation, protocols)
    blocks = _build_theater_blocks(base, interpretation, snapshot, memory_used, protocols)
    render_plan = _build_render_plan(_as_str(base.get("request_id") or _request_id()), interpretation, blocks)
    evidence = _evidence_summary([_as_dict(item) for item in _as_list(base.get("evidence"))])
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
    theater["meta"] = _as_dict(theater.get("meta"))
    theater["meta"]["theater_adapter"] = "prismo_theater_query_payload"
    theater["meta"]["render_block_count"] = len(blocks)
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
