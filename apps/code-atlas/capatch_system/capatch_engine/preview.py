from __future__ import annotations

from pathlib import Path

from .diffing import build_preview_diff_summary
from .transaction import execute_with_state


def preview(ctx, operations):
    executions, state = execute_with_state(ctx, operations)
    messages = [execution.message for _operation, execution, _notes in executions]
    root_dir = Path(getattr(ctx, "root_dir"))
    preview_content = {
        target.relative_to(root_dir).as_posix() if target.is_absolute() else str(target): text
        for target, text in state.items()
    }
    return {
        "messages": messages,
        "preview_content_by_target": preview_content,
        "diff_summary": build_preview_diff_summary(ctx, operations, state),
        "executions": executions,
    }
