from __future__ import annotations

import os
import re
from typing import Any

from prismo_safety import _as_bool, _as_dict, _as_list, _as_str, redact_secrets


ALLOWED_RENDER_BLOCK_TYPES = {
    "hero_response",
    "executive_brief",
    "next_best_action",
    "protocol_ladder",
    "procedural_steps",
    "procedural_recipe",
    "evidence_board",
    "evidence_cards",
    "risk_matrix",
    "timeline",
    "flow_diagram",
    "comparison_board",
    "memory_trace",
    "authority_strip",
    "context_cards",
    "insight_chips",
    "technical_drawer",
    "action_bar",
    "error_recovery",
    "loading_state",
    "feedback_dock",
    "direct_answer_card",
    "authority_map",
    "impact_map",
    "runtime_map",
    "improvement_brief_board",
    "context_pack_explorer",
    "diff_view",
    "checklist",
    "chart_spec",
}

CHART_UNSAFE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)\bfunction\s*\("),
    re.compile(r"(?i)=>"),
    re.compile(r"(?i)document\.cookie|localStorage|sessionStorage|indexedDB|XMLHttpRequest|fetch\s*\("),
    re.compile(r"(?i)<\s*script|javascript:"),
    re.compile(r"(?i)https?://|file://|[A-Za-z]:\\"),
    re.compile(r"(?i)\b(GEMINI_API_KEY|GOOGLE_API_KEY|CLOUDFLARE_API_TOKEN|DATABASE_URL)\b"),
]


def safe_block(message: str = "Bloque visual bloqueado porque no cumplió las reglas de seguridad.") -> dict[str, Any]:
    return {
        "id": "blocked_render_block",
        "type": "direct_answer_card",
        "title": "Bloque visual bloqueado",
        "description": message,
        "priority": "supporting",
        "layout": "full",
        "safety": _safety(sanitized=True),
        "data": {"answer": message, "blocked": True},
    }


def _safety(sanitized: bool = True, interactive: bool = False) -> dict[str, Any]:
    return {
        "trusted": False,
        "sanitized": sanitized,
        "interactive": interactive,
        "allows_scripts": False,
        "allows_network": False,
        "allows_forms": False,
        "reason": "PRISMO v1 render block sanitized server-side.",
    }


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(_stringify(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_stringify(item) for item in value)
    return str(value)


def _contains_chart_risk(value: Any) -> bool:
    text = _stringify(value)
    return any(pattern.search(text) for pattern in CHART_UNSAFE_PATTERNS)


def _clean_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_secrets(value)
    if isinstance(value, list):
        return [_clean_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _clean_value(item) for key, item in value.items()}
    return value


def _normalized_non_object_block(block: Any, index: int) -> dict[str, Any]:
    return {
        "id": f"normalized_non_object_block_{index + 1}",
        "type": "direct_answer_card",
        "title": "Bloque visual normalizado",
        "priority": "supporting",
        "layout": "full",
        "safety": _safety(sanitized=True),
        "data": {"answer": redact_secrets(_as_str(block))},
    }


def normalize_block(block: Any, index: int = 0) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    if not isinstance(block, dict):
        events.append({"code": "RENDER_BLOCK_NOT_OBJECT", "message": "Render block no es objeto."})
        return _normalized_non_object_block(block, index), events

    block_type = str(block.get("type") or "")
    if block_type not in ALLOWED_RENDER_BLOCK_TYPES:
        events.append({"code": "RENDER_BLOCK_TYPE_BLOCKED", "message": f"Render block desconocido bloqueado: {block_type}"})
        return safe_block(), events

    normalized = _clean_value(block)
    normalized = _as_dict(normalized)
    normalized["id"] = redact_secrets(str(normalized.get("id") or f"block_{index + 1:02d}"))
    normalized["type"] = block_type
    normalized["title"] = redact_secrets(str(normalized.get("title") or block_type.replace("_", " ").title()))
    normalized["description"] = redact_secrets(str(normalized.get("description") or ""))
    priority = normalized.get("priority")
    normalized["priority"] = priority if priority in {"primary", "secondary", "supporting"} or isinstance(priority, (int, float)) else "supporting"
    normalized["layout"] = normalized.get("layout") if normalized.get("layout") in {"full", "half", "third", "drawer", "inline"} else "half"
    raw_safety = _as_dict(normalized.get("safety"))
    normalized["safety"] = _safety(sanitized=True, interactive=_as_bool(raw_safety.get("interactive"), False))
    raw_data = normalized.get("data")
    if isinstance(raw_data, dict):
        normalized["data"] = _as_dict(_clean_value(raw_data))
    elif raw_data is None:
        normalized["data"] = {}
    else:
        normalized["data"] = {"value": redact_secrets(_as_str(raw_data))}

    if block_type == "chart_spec" and _contains_chart_risk(normalized.get("data")):
        events.append({"code": "CHART_SPEC_BLOCKED", "message": "chart_spec bloqueado porque contenía JS, HTML, red externa, secreto o ruta sensible."})
        return safe_block(), events

    return normalized, events


def sanitize_render_blocks(blocks: Any, max_blocks: int | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw_blocks = _as_list(blocks)
    events: list[dict[str, Any]] = []
    if blocks is not None and not isinstance(blocks, list):
        events.append({"code": "RENDER_BLOCKS_NOT_ARRAY", "message": "render_blocks no era una lista."})
    if max_blocks is None:
        try:
            max_blocks = int(os.environ.get("PRISMO_AI_MAX_RENDER_BLOCKS", "12"))
        except ValueError:
            max_blocks = 12
    sanitized: list[dict[str, Any]] = []
    for index, block in enumerate(raw_blocks[: max(0, max_blocks)]):
        clean, block_events = normalize_block(block, index=index)
        sanitized.append(clean)
        events.extend(block_events)
    if len(raw_blocks) > max_blocks:
        events.append({"code": "RENDER_BLOCKS_TRUNCATED", "message": f"Render blocks limitados a {max_blocks}."})
    if not sanitized:
        sanitized.append(safe_block("PRISMO no recibió bloques visuales válidos."))
    return sanitized, events
