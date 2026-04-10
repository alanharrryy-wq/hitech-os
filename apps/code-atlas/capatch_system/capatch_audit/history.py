from __future__ import annotations

from pathlib import Path
from typing import Any

from .renderers import read_json, write_json


def history_index_path(root_dir: Path) -> Path:
    return Path(root_dir).resolve() / "reports/patch_history/index.json"


def load_history_index(root_dir: Path) -> dict[str, Any]:
    payload = read_json(history_index_path(root_dir), {"events": []})
    if not isinstance(payload, dict):
        return {"events": []}
    events = payload.get("events")
    if not isinstance(events, list):
        payload["events"] = []
    return payload


def append_history_event(root_dir: Path, event: dict[str, Any]) -> dict[str, Any]:
    root_dir = Path(root_dir).resolve()
    payload = load_history_index(root_dir)
    events = payload.setdefault("events", [])
    event_key = (event.get("event_type"), event.get("run_id"), event.get("checkpoint_id"), event.get("status"))
    existing = {
        (item.get("event_type"), item.get("run_id"), item.get("checkpoint_id"), item.get("status"))
        for item in events
        if isinstance(item, dict)
    }
    if event_key not in existing:
        events.append(dict(event))
    payload["updated_at"] = event.get("timestamp")
    write_json(history_index_path(root_dir), payload)
    return payload
