from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BackupEntry:
    original_path: str
    backup_path: str

    def as_dict(self) -> dict[str, str]:
        return {
            "original_path": self.original_path,
            "backup_path": self.backup_path,
        }


@dataclass(slots=True)
class RollbackManifest:
    rollback_token: str
    root_dir: str
    created_at: str
    operations_count: int
    touched_files: list[str] = field(default_factory=list)
    backup_entries: list[BackupEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rollback_token": self.rollback_token,
            "root_dir": self.root_dir,
            "created_at": self.created_at,
            "operations_count": self.operations_count,
            "touched_files": list(self.touched_files),
            "backup_entries": [entry.as_dict() for entry in self.backup_entries],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RollbackManifest":
        entries = [
            BackupEntry(
                original_path=str(item.get("original_path", "")),
                backup_path=str(item.get("backup_path", "")),
            )
            for item in list(payload.get("backup_entries", []))
            if isinstance(item, dict)
        ]
        return cls(
            rollback_token=str(payload.get("rollback_token", "")),
            root_dir=str(payload.get("root_dir", "")),
            created_at=str(payload.get("created_at", "")),
            operations_count=max(0, int(payload.get("operations_count", 0))),
            touched_files=[str(item) for item in list(payload.get("touched_files", []))],
            backup_entries=entries,
        )
