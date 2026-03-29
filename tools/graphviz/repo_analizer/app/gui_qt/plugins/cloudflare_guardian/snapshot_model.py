from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from typing import Any, Callable

SNAPSHOT_DEFAULTS: dict[str, Any] = {
    "repo_root": "",
    "repo_name": "",
    "repo_ready": False,
    "index_file_count": 0,
    "index_ext_count": 0,
    "index_elapsed_sec": 0.0,
    "active_scope": "",
    "active_extension": "",
    "query_text": "",
    "results_count": 0,
    "current_preview_relpath": "",
    "current_preview_path": "",
    "current_preview_kind": "",
    "nav_can_go_back": False,
    "nav_can_go_forward": False,
    "bookmarks_count": 0,
    "startup_status": "",
    "warning_count": 0,
    "plugin_count": 0,
    "status_text": "",
    "subtitle": "",
    "nodes": [],
    "edges": [],
    "hotspots": [],
    "focus_node_id": "",
}
SNAPSHOT_FIELDS: tuple[str, ...] = tuple(SNAPSHOT_DEFAULTS.keys())


def empty_snapshot() -> dict[str, Any]:
    snapshot = {}
    for key, value in SNAPSHOT_DEFAULTS.items():
        snapshot[key] = list(value) if isinstance(value, list) else value
    return snapshot


def coerce_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def coerce_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


def coerce_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value.strip()))
        except ValueError:
            return 0
    return 0


def coerce_float(value: Any) -> float:
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return 0.0
    return 0.0


def coerce_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    return []


def format_elapsed(value: Any) -> str:
    elapsed = coerce_float(value)
    if elapsed <= 0.0:
        return "0.0s"
    if elapsed < 10.0:
        return f"{elapsed:.2f}s"
    return f"{elapsed:.1f}s"


def normalize_snapshot(
    snapshot: Any,
    *,
    snapshot_payload_fn: Callable[[Any], Any] | None = None,
) -> dict[str, Any]:
    if snapshot is None:
        return empty_snapshot()

    if isinstance(snapshot, Mapping):
        raw = dict(snapshot)
    elif snapshot_payload_fn is not None:
        try:
            raw = coerce_mapping(snapshot_payload_fn(snapshot))
        except Exception:
            raw = {}
    elif is_dataclass(snapshot):
        raw = asdict(snapshot)
    else:
        raw = {key: getattr(snapshot, key) for key in SNAPSHOT_FIELDS if hasattr(snapshot, key)}

    normalized = empty_snapshot()
    normalized["repo_root"] = coerce_string(raw.get("repo_root"))
    normalized["repo_name"] = coerce_string(raw.get("repo_name"))
    normalized["repo_ready"] = coerce_bool(raw.get("repo_ready"))
    normalized["index_file_count"] = coerce_int(raw.get("index_file_count"))
    normalized["index_ext_count"] = coerce_int(raw.get("index_ext_count"))
    normalized["index_elapsed_sec"] = coerce_float(raw.get("index_elapsed_sec"))
    normalized["active_scope"] = coerce_string(raw.get("active_scope"))
    normalized["active_extension"] = coerce_string(raw.get("active_extension"))
    normalized["query_text"] = coerce_string(raw.get("query_text"))
    normalized["results_count"] = coerce_int(raw.get("results_count"))
    normalized["current_preview_relpath"] = coerce_string(raw.get("current_preview_relpath"))
    normalized["current_preview_path"] = coerce_string(raw.get("current_preview_path"))
    normalized["current_preview_kind"] = coerce_string(raw.get("current_preview_kind"))
    normalized["nav_can_go_back"] = coerce_bool(raw.get("nav_can_go_back"))
    normalized["nav_can_go_forward"] = coerce_bool(raw.get("nav_can_go_forward"))
    normalized["bookmarks_count"] = coerce_int(raw.get("bookmarks_count"))
    normalized["startup_status"] = coerce_string(raw.get("startup_status"))
    normalized["warning_count"] = coerce_int(raw.get("warning_count"))
    normalized["plugin_count"] = coerce_int(raw.get("plugin_count"))
    normalized["status_text"] = coerce_string(raw.get("status_text"))
    normalized["subtitle"] = coerce_string(raw.get("subtitle"))
    normalized["nodes"] = coerce_list(raw.get("nodes"))
    normalized["edges"] = coerce_list(raw.get("edges"))
    normalized["hotspots"] = coerce_list(raw.get("hotspots"))
    normalized["focus_node_id"] = coerce_string(raw.get("focus_node_id"))
    return normalized


__all__ = [
    "SNAPSHOT_DEFAULTS",
    "SNAPSHOT_FIELDS",
    "coerce_bool",
    "coerce_float",
    "coerce_int",
    "coerce_list",
    "coerce_mapping",
    "coerce_string",
    "empty_snapshot",
    "format_elapsed",
    "normalize_snapshot",
]
