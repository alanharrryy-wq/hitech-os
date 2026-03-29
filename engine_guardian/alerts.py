from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .state_store import StateStore, utc_now_iso


@dataclass
class AlertBus:
    state_store: StateStore

    def emit(self, level: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        record = {
            "timestamp_utc": utc_now_iso(),
            "level": level.upper(),
            "message": message,
            "context": context or {},
        }
        self.state_store.append_jsonl(self.state_store.last_actions_path, record)
        return record

    def snapshot(self, name: str, payload: Dict[str, Any]) -> str:
        path = self.state_store.write_snapshot(name=name, payload=payload)
        self.emit("INFO", f"Snapshot written: {path.name}", {"path": str(path)})
        return str(path)
