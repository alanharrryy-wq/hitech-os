from __future__ import annotations

from pathlib import Path

from capatch_contracts.operations import OperationSpec
from capatch_fs.atomic_io import read_file_utf8, write_file_if_changed
from capatch_fs.paths import resolve_target_file, resolve_target_path
from capatch_ops.registry import execute_operation

from .support_resolution import materialize_support_payload


def execute_with_state(ctx: object, operations: list[OperationSpec], base_state: dict[Path, str] | None = None):
    state: dict[Path, str] = {} if base_state is None else dict(base_state)
    executions = []
    root_dir = Path(getattr(ctx, "root_dir"))

    def run_one(operation: OperationSpec):
        if operation.type == "ApplySet":
            for child in operation.payload.get("operations") or []:
                run_one(child)
            return
        if operation.type in {"AssertFileExists", "AssertFileNotExists"}:
            target = resolve_target_path(root_dir, operation.file)
            execution = execute_operation(target, None, operation)
            executions.append((operation, execution, []))
            return
        target = resolve_target_file(root_dir, operation.file)
        content = state.get(target)
        if content is None:
            content = read_file_utf8(target)
        operation_to_run = operation
        support_notes: list[str] = []
        payload, support_notes = materialize_support_payload(ctx, target, content, operation)
        if payload != operation.payload:
            operation_to_run = OperationSpec(
                type=operation.type,
                label=operation.label,
                file=operation.file,
                payload=payload,
                schema_version=operation.schema_version,
                idempotency_class=operation.idempotency_class,
                reversibility=operation.reversibility,
            )
        execution = execute_operation(target, content, operation_to_run)
        if execution.final_text is not None:
            state[target] = execution.final_text
        executions.append((operation, execution, support_notes))

    for operation in operations:
        run_one(operation)
    return executions, state


def apply_writes(executions) -> None:
    for _operation, execution, _notes in executions:
        if execution.mutates_file and execution.original_content is not None and execution.final_text is not None:
            write_file_if_changed(execution.target, execution.original_content, execution.final_text)
