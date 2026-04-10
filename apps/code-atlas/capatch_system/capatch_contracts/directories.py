from __future__ import annotations

from pathlib import Path

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


def build_report_paths(root_dir: Path) -> dict[str, Path]:
    root_dir = Path(root_dir)
    return {path_value.replace("/", "_"): root_dir / path_value for path_value in REPORT_DIRS}


def build_mandatory_output_paths(root_dir: Path) -> dict[str, Path]:
    root_dir = Path(root_dir)
    return {name: root_dir / relative_path for name, relative_path in MANDATORY_OUTPUT_FILES.items()}
