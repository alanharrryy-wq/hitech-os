from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable

from capatch_contracts.operations import MUTATING_OPERATION_TYPES, OperationSpec

from .guards import ensure_path_within_root
from .paths import resolve_target_file


def make_checkpoint_backup(path_value: Path, checkpoint_root: Path, root_dir: Path) -> Path:
    ensure_path_within_root(root_dir, path_value)
    relative_path = path_value.resolve().relative_to(root_dir.resolve())
    backup_path = checkpoint_root / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path_value, backup_path)
    return backup_path


def _flatten_operations(operations: Iterable[OperationSpec]) -> list[OperationSpec]:
    items: list[OperationSpec] = []
    for operation in operations:
        if operation.type == "ApplySet":
            items.extend(_flatten_operations(operation.payload.get("operations") or []))
        else:
            items.append(operation)
    return items


def build_session_checkpoints(ctx: object, operations: Iterable[OperationSpec]) -> dict[Path, Path]:
    checkpoint_dir = Path(getattr(ctx, "checkpoint_dir"))
    root_dir = Path(getattr(ctx, "root_dir"))
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoints: dict[Path, Path] = {}
    for operation in _flatten_operations(operations):
        if operation.type not in MUTATING_OPERATION_TYPES:
            continue
        target = resolve_target_file(root_dir, operation.file)
        if target not in checkpoints:
            checkpoints[target] = make_checkpoint_backup(target, checkpoint_dir, root_dir)
    return checkpoints


def restore_session_checkpoints(checkpoints: dict[Path, Path]) -> list[Path]:
    restored: list[Path] = []
    for target, backup in checkpoints.items():
        shutil.copy2(backup, target)
        restored.append(target)
    return restored
