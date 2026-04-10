from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .renderers import sha256_file


@dataclass(slots=True)
class RollbackPreview:
    rollback_id: str
    source_run_id: str
    checkpoint_path: str
    files_to_restore: list[str]
    conflicts_with_current_tree: list[dict[str, Any]]
    restore_ok: bool
    warnings: list[str]


def rollback_preview_to_dict(preview: RollbackPreview) -> dict[str, Any]:
    return asdict(preview)


def build_conflict_rows(*, root_dir: Path, files_to_restore: list[str], expected_after_hashes: dict[str, str | None]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relative_path in files_to_restore:
        current_hash = sha256_file(root_dir / relative_path)
        expected_hash = expected_after_hashes.get(relative_path)
        if expected_hash and current_hash and current_hash != expected_hash:
            rows.append(
                {
                    "relative_path": relative_path,
                    "current_hash": current_hash,
                    "expected_hash": expected_hash,
                }
            )
    return rows
