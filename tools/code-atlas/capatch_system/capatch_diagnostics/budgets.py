from __future__ import annotations

"""Helpers de budgets diagnósticos."""

from typing import Any

from ._contracts import (
    DEFAULT_MAX_ARTIFACT_FILES,
    DEFAULT_MAX_LOG_BYTES,
    DEFAULT_MAX_LOG_LINES,
    DEFAULT_MAX_TAIL_FILES,
)
from .session import DiagnosticBudget


def _bounded_int(value: Any, default: int, *, minimum: int) -> int:
    try:
        return max(minimum, int(value or default))
    except Exception:
        return max(minimum, int(default))


def build_diagnostic_budget(args: Any) -> DiagnosticBudget:
    return DiagnosticBudget(
        max_log_lines=_bounded_int(getattr(args, "max_log_lines", DEFAULT_MAX_LOG_LINES), DEFAULT_MAX_LOG_LINES, minimum=10),
        max_log_bytes=_bounded_int(getattr(args, "max_log_bytes", DEFAULT_MAX_LOG_BYTES), DEFAULT_MAX_LOG_BYTES, minimum=4096),
        max_artifact_files=_bounded_int(
            getattr(args, "max_artifact_files", DEFAULT_MAX_ARTIFACT_FILES), DEFAULT_MAX_ARTIFACT_FILES, minimum=1
        ),
        max_tail_files=_bounded_int(getattr(args, "max_tail_files", DEFAULT_MAX_TAIL_FILES), DEFAULT_MAX_TAIL_FILES, minimum=1),
    )
