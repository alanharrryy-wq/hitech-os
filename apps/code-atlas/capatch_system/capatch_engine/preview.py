from __future__ import annotations

from .diffing import build_preview_diff_summary
from .transaction import execute_with_state


def preview(ctx, operations):
    executions, state = execute_with_state(ctx, operations)
    messages = [execution.message for _operation, execution, _notes in executions]
    return {
        "messages": messages,
        "preview_content_by_target": state,
        "diff_summary": build_preview_diff_summary(ctx, operations, state),
        "executions": executions,
    }
