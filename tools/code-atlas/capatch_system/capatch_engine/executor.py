from __future__ import annotations

from capatch_fs.checkpoints import build_session_checkpoints, restore_session_checkpoints
from capatch_fs.hashing import hash_text

from .result_models import OperationResult
from .syntax_validation import validate_content_by_path
from .transaction import apply_writes, execute_with_state


def _changed_line_count(before: str | None, after: str | None) -> int:
    if before is None or after is None:
        return 0
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    count = 0
    length = max(len(before_lines), len(after_lines))
    for idx in range(length):
        left = before_lines[idx] if idx < len(before_lines) else None
        right = after_lines[idx] if idx < len(after_lines) else None
        if left != right:
            count += 1
    return count


def apply(ctx, operations):
    executions, _state = execute_with_state(ctx, operations)
    if getattr(ctx, "dry_run", False):
        return [
            OperationResult(
                operation_label=operation.label,
                operation_type=operation.type,
                target_path=execution.target.as_posix(),
                patch_status="skipped",
                message=execution.message,
                before_hash=hash_text(execution.original_content) if execution.original_content is not None else None,
                after_hash=hash_text(execution.final_text) if execution.final_text is not None else None,
                preview_hash=hash_text(execution.final_text) if execution.final_text is not None else None,
                bytes_before=len(execution.original_content.encode("utf-8")) if execution.original_content is not None else None,
                bytes_after=len(execution.final_text.encode("utf-8")) if execution.final_text is not None else None,
                changed_line_count=_changed_line_count(execution.original_content, execution.final_text),
                support_notes=list(notes),
            )
            for operation, execution, notes in executions
        ]
    checkpoints = build_session_checkpoints(ctx, operations)
    try:
        apply_writes(executions)
        validation_issues = []
        for _operation, execution, _notes in executions:
            if execution.final_text is not None:
                validation_issues.extend(validate_content_by_path(execution.target, execution.final_text))
        if validation_issues:
            raise RuntimeError("; ".join(issue["error"] for issue in validation_issues[:5]))
    except Exception:
        restore_session_checkpoints(checkpoints)
        raise
    results: list[OperationResult] = []
    for operation, execution, notes in executions:
        before_hash = hash_text(execution.original_content) if execution.original_content is not None else None
        after_hash = hash_text(execution.final_text) if execution.final_text is not None else None
        patch_status = "noop" if execution.original_content == execution.final_text else ("applied" if execution.mutates_file else "skipped")
        results.append(
            OperationResult(
                operation_label=operation.label,
                operation_type=operation.type,
                target_path=execution.target.as_posix(),
                patch_status=patch_status,
                message=execution.message,
                before_hash=before_hash,
                after_hash=after_hash,
                preview_hash=after_hash,
                bytes_before=len(execution.original_content.encode("utf-8")) if execution.original_content is not None else None,
                bytes_after=len(execution.final_text.encode("utf-8")) if execution.final_text is not None else None,
                changed_line_count=_changed_line_count(execution.original_content, execution.final_text),
                support_notes=list(notes),
            )
        )
    return results
