from __future__ import annotations

"""Helpers de budgets diagnósticos."""

from typing import Any

from ._contracts import DEFAULT_MAX_LOG_BYTES, DEFAULT_MAX_LOG_LINES
from .session import DiagnosticBudget


def build_diagnostic_budget(args: Any) -> DiagnosticBudget:
    return DiagnosticBudget(
        max_log_lines=max(10, int(getattr(args, "max_log_lines", DEFAULT_MAX_LOG_LINES) or DEFAULT_MAX_LOG_LINES)),
        max_log_bytes=max(4096, int(getattr(args, "max_log_bytes", DEFAULT_MAX_LOG_BYTES) or DEFAULT_MAX_LOG_BYTES)),
    )
