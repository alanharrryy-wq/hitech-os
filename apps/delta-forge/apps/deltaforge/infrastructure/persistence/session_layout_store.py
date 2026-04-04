from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Mapping

from domain.ids import ScopeId, SessionId


class SessionLayoutStore:
    """JSON-backed per-session layout persistence."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self._path.exists():
            return {"sessions": {}}
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return self._normalize(data)

    def save(self, document: Mapping[str, Any]) -> dict[str, Any]:
        normalized = self._normalize(document)
        self._write_json(normalized)
        return normalized

    def list_layouts(self) -> dict[str, Any]:
        return dict(self.load()["sessions"])

    def read_layout(self, session_id: SessionId) -> dict[str, Any] | None:
        document = self.load()
        payload = document["sessions"].get(self._id_key(session_id))
        if payload is None:
            return None
        return dict(payload)

    def write_layout(
        self,
        session_id: SessionId,
        *,
        scope_id: ScopeId | None,
        layout: Mapping[str, Any],
        root_dir: str = "",
        ops_source_path: str = "",
        rollback_token: str = "",
        last_result: Mapping[str, Any] | None = None,
        selection: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        document = self.load()
        document["sessions"][self._id_key(session_id)] = {
            "session_id": self._id_key(session_id),
            "scope_id": None if scope_id is None else self._id_key(scope_id),
            "layout": dict(layout),
            "root_dir": str(root_dir or ""),
            "ops_source_path": str(ops_source_path or ""),
            "rollback_token": str(rollback_token or ""),
            "last_result": dict(last_result or {}),
            "selection": dict(selection or {}),
        }
        return self.save(document)

    def delete_layout(self, session_id: SessionId) -> dict[str, Any]:
        document = self.load()
        document["sessions"].pop(self._id_key(session_id), None)
        return self.save(document)

    def _normalize(self, document: Mapping[str, Any]) -> dict[str, Any]:
        sessions = {}
        for key, value in dict(document.get("sessions", {})).items():
            record = dict(value)
            record["session_id"] = str(record.get("session_id", key))
            if record.get("scope_id") is not None:
                record["scope_id"] = str(record["scope_id"])
            record["layout"] = dict(record.get("layout", {}))
            record["root_dir"] = str(record.get("root_dir", ""))
            record["ops_source_path"] = str(record.get("ops_source_path", ""))
            record["rollback_token"] = str(record.get("rollback_token", ""))
            record["last_result"] = dict(record.get("last_result", {}))
            record["selection"] = dict(record.get("selection", {}))
            sessions[str(key)] = record
        return {"sessions": sessions}

    def _write_json(self, data: Mapping[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(self._path.parent)) as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            temp_name = handle.name
        Path(temp_name).replace(self._path)

    def _id_key(self, value: Any) -> str:
        return str(value)
