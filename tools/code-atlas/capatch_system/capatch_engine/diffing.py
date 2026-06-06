from __future__ import annotations

from pathlib import Path
from typing import Iterable

from capatch_contracts.operations import MUTATING_OPERATION_TYPES, OperationSpec
from capatch_fs.atomic_io import read_file_utf8
from capatch_fs.paths import resolve_target_file
from capatch_ops.composite_ops import flatten_operation_specs


def count_mutating_ops_for_target(ctx: object, operations: Iterable[OperationSpec], target: Path) -> int:
    count = 0
    root_dir = Path(getattr(ctx, "root_dir"))
    for operation in flatten_operation_specs(operations):
        if operation.type not in MUTATING_OPERATION_TYPES:
            continue
        if resolve_target_file(root_dir, operation.file) == target:
            count += 1
    return count


def build_preview_diff_summary(ctx: object, operations: Iterable[OperationSpec], preview_content_by_target: dict[Path, str]) -> list[str]:
    summaries: list[str] = []
    root_dir = Path(getattr(ctx, "root_dir"))
    for target in sorted(preview_content_by_target):
        original = read_file_utf8(target)
        final = preview_content_by_target[target]
        if original == final:
            continue
        line_delta = len(final.splitlines()) - len(original.splitlines())
        char_delta = len(final) - len(original)
        op_count = count_mutating_ops_for_target(ctx, operations, target)
        relative = target.resolve().relative_to(root_dir.resolve()).as_posix()
        summaries.append(f"{relative} | ops={op_count} | line_delta={line_delta:+d} | char_delta={char_delta:+d}")
    if not summaries:
        summaries.append("sin cambios materiales.")
    return summaries
