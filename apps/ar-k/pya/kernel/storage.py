from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pya.contracts.artifact_contracts import build_artifact
from pya.contracts.base import stable_hash
from pya.contracts.snapshot_contracts import build_delta, build_snapshot
from pya.system.ownership import may_read, may_write


class GovernedStorage:
    def __init__(self, *, paths: "RuntimePaths", execution_id: str, timestamp: str):
        self.paths = paths
        self.execution_id = execution_id
        self.timestamp = timestamp
        self._written: dict[str, list[str]] = {}

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def registry_path(self, registry_name: str) -> Path:
        return self.paths.registries / f"{registry_name}.json"

    def index_path(self, index_name: str) -> Path:
        return self.paths.indices / f"{index_name}.json"

    def read_registry(self, engine_id: str, registry_name: str, default: Any = None) -> Any:
        if not may_read(engine_id, registry_name):
            raise PermissionError(f"{engine_id} may not read registry {registry_name}")
        return self._read_json(self.registry_path(registry_name), [] if default is None else default)

    def write_registry(self, engine_id: str, registry_name: str, payload: Any) -> Path:
        if not may_write(engine_id, registry_name):
            raise PermissionError(f"{engine_id} may not write registry {registry_name}")
        path = self.registry_path(registry_name)
        self._write_json(path, payload)
        self._written.setdefault(engine_id, []).append(registry_name)
        return path

    def read_index(self, engine_id: str, index_name: str, default: Any = None) -> Any:
        if not may_read(engine_id, index_name):
            raise PermissionError(f"{engine_id} may not read index {index_name}")
        return self._read_json(self.index_path(index_name), [] if default is None else default)

    def write_index(self, engine_id: str, index_name: str, payload: Any) -> Path:
        if not may_write(engine_id, index_name):
            raise PermissionError(f"{engine_id} may not write index {index_name}")
        path = self.index_path(index_name)
        self._write_json(path, payload)
        self._written.setdefault(engine_id, []).append(index_name)
        return path

    def write_artifact(self, engine_id: str, family: str, name: str, payload: Any) -> dict[str, Any]:
        target = self.paths.artifacts / family / name
        self._write_json(target, payload)
        return build_artifact(
            family=family,
            path=str(target),
            producer=engine_id,
            snapshot_id=self.execution_id,
            content_hash=stable_hash(payload),
            created_at=self.timestamp,
        )

    def write_snapshot(self, engine_id: str, family: str, payload: Any) -> dict[str, Any]:
        target = self.paths.snapshots / f"{family}_{self.execution_id}.json"
        snapshot = build_snapshot(family=family, payload=payload, content_hash=stable_hash(payload), created_at=self.timestamp)
        self._write_json(target, snapshot)
        self._written.setdefault(engine_id, []).append("snapshots")
        return snapshot

    def write_delta(self, engine_id: str, family: str, payload: Any) -> dict[str, Any]:
        target = self.paths.deltas / f"{family}_{self.execution_id}.json"
        delta = build_delta(snapshot_id=self.execution_id, family=family, payload=payload, content_hash=stable_hash(payload), created_at=self.timestamp)
        self._write_json(target, delta)
        self._written.setdefault(engine_id, []).append("deltas")
        return delta

    def written_registries(self, engine_id: str) -> list[str]:
        return list(self._written.get(engine_id, []))
