from __future__ import annotations

"""Compat bridge hacia capatch_contracts.

Mantiene a capatch_diagnostics pegado al vocabulario del Master Spec.
Si la subparte A ya existe, consume sus exports públicos. Si aún no existe,
usa el contrato congelado en el spec como scaffold temporal, sin inventar
nombres alternos.
"""

from pathlib import Path

try:  # pragma: no cover - depende de otra subparte
    from capatch_contracts.constants import (  # type: ignore
        DEFAULT_COMMAND_TIMEOUT_SECONDS,
        DEFAULT_MAX_ARTIFACT_FILES,
        DEFAULT_MAX_FIX_PROPOSALS_TO_EXECUTE,
        DEFAULT_MAX_LOG_BYTES,
        DEFAULT_MAX_LOG_LINES,
        DEFAULT_MAX_TAIL_FILES,
        DEFAULT_REPORT_BUNDLE_FORMAT,
        MANDATORY_OUTPUT_FILES,
    )
    from capatch_contracts.directories import REPORT_DIRS  # type: ignore
    from capatch_contracts.enums import (  # type: ignore
        APP_KINDS,
        EXECUTION_MODES,
        PLUGIN_KINDS,
        PRIORITIES,
        RISK_LEVELS,
        RISK_TIERS,
        RUNTIME_PHASES,
        SEVERITIES,
    )
except Exception:  # pragma: no cover - scaffold de Fase 0 mientras A no exista
    DEFAULT_MAX_LOG_LINES = 200
    DEFAULT_MAX_LOG_BYTES = 262_144
    DEFAULT_MAX_ARTIFACT_FILES = 64
    DEFAULT_MAX_TAIL_FILES = 32
    DEFAULT_COMMAND_TIMEOUT_SECONDS = 45
    DEFAULT_MAX_FIX_PROPOSALS_TO_EXECUTE = 2
    DEFAULT_REPORT_BUNDLE_FORMAT = "md"

    RUNTIME_PHASES = (
        "resolve-target",
        "collect",
        "enrich",
        "analyze",
        "recommend",
        "fix",
        "verify",
        "export",
    )
    EXECUTION_MODES = (
        "patch-run",
        "diagnose",
        "collect-only",
        "verify-only",
        "support-bundle",
        "fix-plan",
        "apply-fixes",
        "rollback-preview",
        "rollback-apply",
        "plugin-list",
        "plugin-health",
        "plugin-enable",
        "plugin-disable",
        "show-run",
        "list-checkpoints",
    )
    PLUGIN_KINDS = (
        "guard",
        "target-detector",
        "context-enricher",
        "collector",
        "analyzer",
        "recommender",
        "fixer",
        "verifier",
        "exporter",
    )
    SEVERITIES = ("info", "warn", "error", "critical")
    PRIORITIES = ("low", "normal", "high", "urgent")
    RISK_LEVELS = ("low", "medium", "high", "critical")
    RISK_TIERS = ("safe", "guarded", "high-risk", "blocked")
    APP_KINDS = ("auto", "unknown", "mixed", "python", "node", "web", "desktop")
    REPORT_DIRS = (
        "reports/diagnostics",
        "reports/findings",
        "reports/verification",
        "reports/bundles",
        "reports/telemetry",
        "reports/confidence",
        "reports/decision_ledger",
        "reports/patch_history",
        "reports/patch_runs",
        "reports/checkpoints",
        "reports/rollback",
        "reports/baselines",
        "reports/cache",
    )
    MANDATORY_OUTPUT_FILES = {
        "diagnostic_session_json": "reports/diagnostics/diagnostic_session.json",
        "diagnostic_session_md": "reports/diagnostics/diagnostic_session.md",
        "support_bundle_json": "reports/bundles/support_bundle.json",
        "support_bundle_md": "reports/bundles/support_bundle.md",
        "support_bundle_v2_json": "reports/bundles/support_bundle_v2.json",
        "support_bundle_v2_md": "reports/bundles/support_bundle_v2.md",
        "confidence_summary_json": "reports/confidence/confidence_summary.json",
        "confidence_summary_md": "reports/confidence/confidence_summary.md",
        "intervention_gates_json": "reports/telemetry/intervention_gates.json",
        "intervention_gates_md": "reports/telemetry/intervention_gates.md",
        "patch_history_index_json": "reports/patch_history/index.json",
        "fix_execution_json": "reports/findings/fix_execution.json",
        "fix_execution_md": "reports/findings/fix_execution.md",
        "before_after_verification_json": "reports/verification/before_after_verification.json",
        "before_after_verification_md": "reports/verification/before_after_verification.md",
    }


def report_path(base_dir: Path, key: str) -> Path:
    relative = MANDATORY_OUTPUT_FILES[key]
    return (base_dir / relative).resolve()
