from __future__ import annotations

import json
from copy import deepcopy
from typing import Any


def default_behavior_binding() -> dict[str, Any]:
    return {
        "event": "clicked",
        "action_type": "none",
        "command_id": "",
        "target_panel_id": "",
        "task_ref": "",
        "payload": {},
    }


def _coerce_bool(value: Any, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    if value is None:
        return default
    return bool(value)


def _coerce_text(value: Any, *, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def default_widget_props(panel_type: str, *, title: str = "", text: str = "") -> dict[str, Any]:
    normalized_type = str(panel_type or "").strip().lower()
    base = {
        "text": str(text or ""),
        "tooltip": "",
        "object_name": "",
        "enabled": True,
        "visible": True,
        "checkable": False,
        "checked": False,
        "icon_name": "",
        "style_variant": "default",
    }
    if normalized_type == "button_control":
        base["text"] = str(text or title or "Execute")
    elif normalized_type in {"action_buttons", "toolbar_controls"}:
        base["style_variant"] = "muted"
    elif normalized_type in {"error_state_shell"}:
        base["style_variant"] = "warning"
    return base


def normalize_widget_props(panel_type: str, payload: Any) -> dict[str, Any]:
    defaults = default_widget_props(panel_type)
    candidate = payload if isinstance(payload, dict) else {}
    merged = deepcopy(defaults)
    merged.update({str(key): value for key, value in candidate.items()})
    merged["text"] = _coerce_text(merged.get("text"), default=defaults["text"])
    merged["tooltip"] = _coerce_text(merged.get("tooltip"), default="")
    merged["object_name"] = _coerce_text(merged.get("object_name"), default="")
    merged["enabled"] = _coerce_bool(merged.get("enabled"), default=True)
    merged["visible"] = _coerce_bool(merged.get("visible"), default=True)
    merged["checkable"] = _coerce_bool(merged.get("checkable"), default=False)
    merged["checked"] = _coerce_bool(merged.get("checked"), default=False)
    if not merged["checkable"]:
        merged["checked"] = False
    merged["icon_name"] = _coerce_text(merged.get("icon_name"), default="")
    merged["style_variant"] = _coerce_text(merged.get("style_variant"), default="default").strip().lower() or "default"
    return merged


def normalize_behavior_binding(payload: Any) -> dict[str, Any]:
    defaults = default_behavior_binding()
    candidate = payload if isinstance(payload, dict) else {}
    merged = deepcopy(defaults)
    merged.update({str(key): value for key, value in candidate.items()})
    merged["event"] = _coerce_text(merged.get("event"), default="clicked").strip().lower() or "clicked"
    merged["action_type"] = _coerce_text(merged.get("action_type"), default="none").strip().lower() or "none"
    merged["command_id"] = _coerce_text(merged.get("command_id"), default="")
    merged["target_panel_id"] = _coerce_text(merged.get("target_panel_id"), default="")
    merged["task_ref"] = _coerce_text(merged.get("task_ref"), default="")
    payload_value = merged.get("payload")
    if isinstance(payload_value, dict):
        merged["payload"] = payload_value
    else:
        merged["payload"] = {"value": payload_value} if payload_value not in (None, "", []) else {}
    return merged


def parse_behavior_payload(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    if not raw:
        return {}
    parsed = json.loads(raw)
    if isinstance(parsed, dict):
        return parsed
    return {"value": parsed}


def behavior_summary(binding: Any) -> str:
    normalized = normalize_behavior_binding(binding)
    action_type = normalized["action_type"]
    if action_type == "none":
        return "Behavior: none"
    fragments = [f"Behavior: {action_type}"]
    if normalized["command_id"]:
        fragments.append(f"command={normalized['command_id']}")
    if normalized["target_panel_id"]:
        fragments.append(f"target={normalized['target_panel_id']}")
    if normalized["task_ref"]:
        fragments.append(f"task={normalized['task_ref']}")
    payload = normalized.get("payload", {})
    if isinstance(payload, dict) and payload:
        fragments.append(f"payload_keys={len(payload)}")
    return " · ".join(fragments)
