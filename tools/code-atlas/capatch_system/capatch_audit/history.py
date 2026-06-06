from __future__ import annotations

from pathlib import Path
from typing import Any

from capatch_contracts.versions import PATCH_HISTORY_SCHEMA_VERSION, PATCH_RUN_SCHEMA_VERSION

from .renderers import read_json, write_json


_HISTORY_SCHEMA_VERSION = PATCH_HISTORY_SCHEMA_VERSION


def history_index_path(root_dir: Path) -> Path:
    return Path(root_dir).resolve() / "reports/patch_history/index.json"


def _empty_history(root_dir: Path) -> dict[str, Any]:
    return {
        "schema_version": _HISTORY_SCHEMA_VERSION,
        "patch_run_schema_version": PATCH_RUN_SCHEMA_VERSION,
        "root_dir": str(Path(root_dir).resolve()),
        "updated_at": None,
        "events": [],
        "stats": {
            "total_events": 0,
            "patch_runs": 0,
            "rollbacks": 0,
            "baselines": 0,
            "applied": 0,
            "failed": 0,
            "rolled_back": 0,
        },
    }


def _event_id(event: dict[str, Any]) -> str:
    event_type = str(event.get("event_type") or "event")
    run_id = str(event.get("run_id") or "")
    checkpoint_id = str(event.get("checkpoint_id") or "")
    baseline_id = str(event.get("baseline_id") or "")
    status = str(event.get("status") or "")
    timestamp = str(event.get("timestamp") or "")
    if run_id or checkpoint_id or baseline_id or status:
        return "::".join([event_type, run_id, checkpoint_id, baseline_id, status])
    return "::".join([event_type, timestamp])


def _normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    payload = dict(event)
    payload["event_id"] = str(payload.get("event_id") or _event_id(payload))
    payload["event_type"] = str(payload.get("event_type") or "event")
    payload["timestamp"] = payload.get("timestamp")
    payload["run_id"] = payload.get("run_id")
    payload["checkpoint_id"] = payload.get("checkpoint_id")
    payload["baseline_id"] = payload.get("baseline_id")
    payload["trace_id"] = payload.get("trace_id") or payload.get("run_id")
    payload["status"] = payload.get("status")
    payload["system_status"] = payload.get("system_status")
    payload["detail"] = str(payload.get("detail") or "")
    payload["source_command"] = payload.get("source_command")
    payload["actor"] = payload.get("actor")
    payload["report_refs"] = dict(payload.get("report_refs") or {})
    return payload


def _recompute_stats(payload: dict[str, Any]) -> dict[str, Any]:
    events = [item for item in list(payload.get("events") or []) if isinstance(item, dict)]
    stats = {
        "total_events": len(events),
        "patch_runs": sum(1 for item in events if item.get("event_type") == "patch-run"),
        "rollbacks": sum(1 for item in events if item.get("event_type") == "rollback"),
        "baselines": sum(1 for item in events if item.get("event_type") == "baseline"),
        "applied": sum(1 for item in events if item.get("status") == "applied"),
        "failed": sum(1 for item in events if item.get("status") == "failed"),
        "rolled_back": sum(1 for item in events if item.get("status") == "rolled_back"),
    }
    payload["stats"] = stats
    return payload


def load_history_index(root_dir: Path) -> dict[str, Any]:
    root_dir = Path(root_dir).resolve()
    payload = read_json(history_index_path(root_dir), _empty_history(root_dir))
    if not isinstance(payload, dict):
        payload = _empty_history(root_dir)
    payload.setdefault("schema_version", _HISTORY_SCHEMA_VERSION)
    payload.setdefault("patch_run_schema_version", PATCH_RUN_SCHEMA_VERSION)
    payload.setdefault("root_dir", str(root_dir))
    payload.setdefault("updated_at", None)
    events = payload.get("events")
    if not isinstance(events, list):
        events = []
    normalized = [_normalize_event(item) for item in events if isinstance(item, dict)]
    normalized.sort(key=lambda item: (str(item.get("timestamp") or ""), str(item.get("event_id") or "")), reverse=True)
    payload["events"] = normalized
    return _recompute_stats(payload)


def append_history_event(root_dir: Path, event: dict[str, Any]) -> dict[str, Any]:
    root_dir = Path(root_dir).resolve()
    payload = load_history_index(root_dir)
    normalized_event = _normalize_event(event)
    events = [item for item in payload.get("events", []) if isinstance(item, dict)]
    by_id = {str(item.get("event_id") or _event_id(item)): item for item in events}
    by_id[normalized_event["event_id"]] = normalized_event
    payload["events"] = sorted(
        by_id.values(),
        key=lambda item: (str(item.get("timestamp") or ""), str(item.get("event_id") or "")),
        reverse=True,
    )
    payload["updated_at"] = normalized_event.get("timestamp")
    payload = _recompute_stats(payload)
    write_json(history_index_path(root_dir), payload)
    return payload
