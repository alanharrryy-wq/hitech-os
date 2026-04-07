from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from domain.models.rollback_manifest import BackupEntry, RollbackManifest


class BackupStore:
    BACKUP_DIR_NAME = "_deltaforge_backups"
    MANIFEST_NAME = "manifest.json"

    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir).expanduser().resolve()
        self.backup_root = self.root_dir / self.BACKUP_DIR_NAME

    def create_token(self) -> str:
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{stamp}_{uuid4().hex[:6]}"

    def start_manifest(
        self,
        *,
        rollback_token: str,
        operations_count: int,
        touched_files: list[str],
    ) -> RollbackManifest:
        self.token_dir(rollback_token).mkdir(parents=True, exist_ok=True)
        return RollbackManifest(
            rollback_token=rollback_token,
            root_dir=str(self.root_dir),
            created_at=datetime.utcnow().isoformat(),
            operations_count=max(0, int(operations_count)),
            touched_files=list(touched_files),
            backup_entries=[],
        )

    def backup_file(self, manifest: RollbackManifest, original_path: str | Path) -> BackupEntry:
        source = Path(original_path).expanduser().resolve()
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(f"Source file not found for backup: {source}")

        for entry in manifest.backup_entries:
            if Path(entry.original_path).resolve() == source:
                return entry

        relative = self._relative_path(source)
        backup_path = self.token_dir(manifest.rollback_token) / "files" / relative
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, backup_path)

        entry = BackupEntry(original_path=str(source), backup_path=str(backup_path))
        manifest.backup_entries.append(entry)
        return entry

    def write_manifest(self, manifest: RollbackManifest) -> Path:
        manifest_path = self.manifest_path(manifest.rollback_token)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return manifest_path

    def read_manifest(self, rollback_token: str) -> RollbackManifest:
        path = self.manifest_path(rollback_token)
        if not path.exists():
            raise FileNotFoundError(f"Manifest not found for rollback token: {rollback_token}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        return RollbackManifest.from_dict(payload)

    def restore(self, manifest: RollbackManifest) -> tuple[list[str], list[str]]:
        restored: list[str] = []
        errors: list[str] = []
        for entry in manifest.backup_entries:
            source = Path(entry.backup_path)
            target = Path(entry.original_path)
            try:
                if not source.exists():
                    raise FileNotFoundError(f"Backup file not found: {source}")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                restored.append(str(target))
            except Exception as exc:  # pragma: no cover - defensive
                errors.append(f"Failed restoring {target}: {exc}")
        return restored, errors

    def token_dir(self, rollback_token: str) -> Path:
        return self.backup_root / rollback_token

    def manifest_path(self, rollback_token: str) -> Path:
        return self.token_dir(rollback_token) / self.MANIFEST_NAME

    def _relative_path(self, path_value: Path) -> Path:
        try:
            return path_value.relative_to(self.root_dir)
        except ValueError:
            safe = path_value.as_posix().replace(":", "")
            return Path("_external") / safe.lstrip("/")
