from __future__ import annotations

from datetime import datetime
from pathlib import Path

from capatch_contracts.operations import MUTATING_OPERATION_TYPES, READ_ONLY_OPERATION_TYPES, OperationSpec
from capatch_fs.guards import ensure_directory
from capatch_fs.paths import resolve_target_path

from .result_models import PreflightReport
from .syntax_validation import build_syntax_validation_plan


def _risk_summary(operations: list[OperationSpec], target_files: list[str]) -> dict[str, object]:
    file_count = len(set(target_files))
    mutating_count = sum(1 for op in operations if op.type in MUTATING_OPERATION_TYPES)
    reversible = all(op.reversibility in {"full", "partial"} for op in operations)
    if file_count <= 1 and mutating_count <= 3 and reversible:
        tier = "safe"
        level = "low"
    elif file_count <= 4 and mutating_count <= 12 and reversible:
        tier = "guarded"
        level = "medium"
    else:
        tier = "high-risk"
        level = "high"
    return {"risk_tier": tier, "risk_level": level, "file_count": file_count, "mutating_operation_count": mutating_count}


def preflight(ctx, operations):
    ensure_directory(Path(ctx.root_dir))
    run_id = datetime.now().strftime("preflight_%Y%m%d_%H%M%S")
    path_violations = []
    target_files: list[str] = []
    for operation in operations:
        try:
            if operation.type != "ApplySet":
                target = resolve_target_path(Path(ctx.root_dir), operation.file)
                target_files.append(target.relative_to(Path(ctx.root_dir)).as_posix())
            else:
                for child in operation.payload.get("operations") or []:
                    target = resolve_target_path(Path(ctx.root_dir), child.file)
                    target_files.append(target.relative_to(Path(ctx.root_dir)).as_posix())
        except Exception as exc:
            path_violations.append({"operation_label": operation.label, "file": operation.file, "error": str(exc)})
    conflicts = []
    seen_targets: dict[str, set[str]] = {}
    for operation in operations:
        if operation.type == "ApplySet":
            for child in operation.payload.get("operations") or []:
                if child.type in MUTATING_OPERATION_TYPES:
                    seen_targets.setdefault(child.file, set()).add(child.type)
        elif operation.type in MUTATING_OPERATION_TYPES:
            seen_targets.setdefault(operation.file, set()).add(operation.type)
    for file_name, op_types in sorted(seen_targets.items()):
        if len(op_types) > 8:
            conflicts.append({"file": file_name, "reason": "high_operation_density", "operation_types": sorted(op_types)})
    syntax_validation_plan = build_syntax_validation_plan(sorted(set(target_files)))
    risk_summary = _risk_summary(operations, target_files)
    return PreflightReport(
        ok=not path_violations,
        run_id=run_id,
        target_files=sorted(set(target_files)),
        operation_count=len(operations),
        mutating_operation_count=sum(1 for op in operations if op.type in MUTATING_OPERATION_TYPES),
        read_only_operation_count=sum(1 for op in operations if op.type in READ_ONLY_OPERATION_TYPES),
        conflicts=conflicts,
        path_violations=path_violations,
        schema_violations=[],
        syntax_validation_plan=syntax_validation_plan,
        risk_summary=risk_summary,
    )
