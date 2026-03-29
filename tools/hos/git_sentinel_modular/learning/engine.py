from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from ..shared.contracts import ArtifactFinding, ScanResult, SecurityFinding
from ..shared.errors import ConfigurationError
from ..shared.foundation import write_json


def _iso_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(slots=True)
class LearningSnapshot:
    repo_root: str
    last_scan_id: str = ""
    total_scans: int = 0
    file_churn: dict[str, int] = field(default_factory=dict)
    security_rule_hits: dict[str, int] = field(default_factory=dict)
    artifact_category_hits: dict[str, int] = field(default_factory=dict)
    updated_at: str = field(default_factory=_iso_now)

    def validate(self) -> "LearningSnapshot":
        if not isinstance(self.repo_root, str) or not self.repo_root.strip():
            raise ConfigurationError("LearningSnapshot.repo_root must be non-empty.", repo_root=self.repo_root)
        if not isinstance(self.last_scan_id, str):
            raise ConfigurationError("LearningSnapshot.last_scan_id must be a string.", last_scan_id=self.last_scan_id)
        if not isinstance(self.total_scans, int) or self.total_scans < 0:
            raise ConfigurationError("LearningSnapshot.total_scans must be non-negative int.", total_scans=self.total_scans)
        self.file_churn = self._validate_counter_map(self.file_churn, "file_churn")
        self.security_rule_hits = self._validate_counter_map(self.security_rule_hits, "security_rule_hits")
        self.artifact_category_hits = self._validate_counter_map(self.artifact_category_hits, "artifact_category_hits")
        if not isinstance(self.updated_at, str) or not self.updated_at.strip():
            raise ConfigurationError("LearningSnapshot.updated_at must be non-empty.", updated_at=self.updated_at)
        return self

    @staticmethod
    def _validate_counter_map(value: Mapping[str, Any] | dict[str, int], field_name: str) -> dict[str, int]:
        if not isinstance(value, Mapping):
            raise ConfigurationError(f"{field_name} must be mapping-like.", field_name=field_name)
        normalized: dict[str, int] = {}
        for key, count in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ConfigurationError(f"{field_name} contains invalid key.", field_name=field_name, key=repr(key))
            if not isinstance(count, int) or count < 0:
                raise ConfigurationError(f"{field_name} contains invalid counter.", field_name=field_name, key=key, count=count)
            normalized[key] = count
        return normalized

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "repo_root": self.repo_root,
            "last_scan_id": self.last_scan_id,
            "total_scans": self.total_scans,
            "file_churn": dict(sorted(self.file_churn.items())),
            "security_rule_hits": dict(sorted(self.security_rule_hits.items())),
            "artifact_category_hits": dict(sorted(self.artifact_category_hits.items())),
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "LearningSnapshot":
        return cls(
            repo_root=payload.get("repo_root", ""),
            last_scan_id=payload.get("last_scan_id", ""),
            total_scans=int(payload.get("total_scans", 0)),
            file_churn=dict(payload.get("file_churn", {})),
            security_rule_hits=dict(payload.get("security_rule_hits", {})),
            artifact_category_hits=dict(payload.get("artifact_category_hits", {})),
            updated_at=payload.get("updated_at", _iso_now()),
        ).validate()


class SQLiteLearningStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _ensure_schema(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_snapshots (
                    repo_root TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def load_snapshot(self, repo_root: str) -> dict[str, Any]:
        repo_root = str(Path(repo_root).resolve())
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT payload_json FROM learning_snapshots WHERE repo_root = ?",
                (repo_root,),
            ).fetchone()
        if row is None:
            return LearningSnapshot(repo_root=repo_root).validate().to_dict()
        return LearningSnapshot.from_mapping(json.loads(row[0])).to_dict()

    def save_snapshot(self, repo_root: str, payload: Mapping[str, Any]) -> None:
        repo_root = str(Path(repo_root).resolve())
        snapshot = LearningSnapshot.from_mapping({**dict(payload), "repo_root": repo_root})
        encoded = json.dumps(snapshot.to_dict(), ensure_ascii=False, sort_keys=True)
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO learning_snapshots (repo_root, payload_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(repo_root) DO UPDATE SET
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                (repo_root, encoded, snapshot.updated_at),
            )
            conn.commit()

    def update_from_scan(self, scan_result: ScanResult) -> dict[str, Any]:
        current = LearningSnapshot.from_mapping(self.load_snapshot(scan_result.repo_root))
        current.total_scans += 1
        current.last_scan_id = scan_result.scan_id
        current.updated_at = _iso_now()

        for artifact in scan_result.artifact_findings:
            artifact = artifact if isinstance(artifact, ArtifactFinding) else ArtifactFinding(**artifact).validate()
            current.file_churn[artifact.path] = current.file_churn.get(artifact.path, 0) + 1
            current.artifact_category_hits[artifact.category] = current.artifact_category_hits.get(artifact.category, 0) + 1

        for finding in scan_result.security_findings:
            finding = finding if isinstance(finding, SecurityFinding) else SecurityFinding(**finding).validate()
            current.file_churn[finding.path] = current.file_churn.get(finding.path, 0) + 1
            current.security_rule_hits[finding.rule_id] = current.security_rule_hits.get(finding.rule_id, 0) + 1

        payload = current.validate().to_dict()
        self.save_snapshot(scan_result.repo_root, payload)
        return payload

    def export_snapshot_json(self, repo_root: str, output_path: str | Path) -> Path:
        output_path = Path(output_path).resolve()
        payload = self.load_snapshot(repo_root)
        write_json(output_path, payload)
        return output_path
