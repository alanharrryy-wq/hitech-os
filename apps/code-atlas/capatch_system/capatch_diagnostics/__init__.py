from __future__ import annotations

from .loader import PLUGIN_RUNTIME_VERSION, PluginAPI, empty_plugin_state, initialize_plugin_runtime
from .reporting import ensure_report_dirs, write_session_reports, write_support_bundle
from .runtime import build_session, run_diagnostic_command, run_session, run_session_reports
from .session import (
    DiagnosticArtifact,
    DiagnosticBudget,
    DiagnosticSession,
    Finding,
    FixProposal,
    PluginExecutionRecord,
    Recommendation,
    VerificationResult,
    make_session_id,
    to_jsonable,
    utc_now_iso,
)
from .targeting import build_environment_summary, detect_app_kind, resolve_target_path

__all__ = [
    "PLUGIN_RUNTIME_VERSION",
    "PluginAPI",
    "empty_plugin_state",
    "initialize_plugin_runtime",
    "build_session",
    "run_diagnostic_command",
    "run_session",
    "run_session_reports",
    "ensure_report_dirs",
    "write_session_reports",
    "write_support_bundle",
    "DiagnosticArtifact",
    "DiagnosticBudget",
    "DiagnosticSession",
    "Finding",
    "FixProposal",
    "PluginExecutionRecord",
    "Recommendation",
    "VerificationResult",
    "make_session_id",
    "to_jsonable",
    "utc_now_iso",
    "build_environment_summary",
    "detect_app_kind",
    "resolve_target_path",
]
