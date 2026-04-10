from __future__ import annotations

from .directories import MANDATORY_OUTPUT_FILES, REPORT_DIRS

REPORT_FILE_OWNERS = {
    "reports/diagnostics/diagnostic_session.json": "capatch_diagnostics.reporting",
    "reports/diagnostics/diagnostic_session.md": "capatch_diagnostics.reporting",
    "reports/bundles/support_bundle.json": "capatch_diagnostics.reporting",
    "reports/bundles/support_bundle.md": "capatch_diagnostics.reporting",
    "reports/bundles/support_bundle_v2.json": "capatch_policy.decision_ledger",
    "reports/bundles/support_bundle_v2.md": "capatch_policy.decision_ledger",
    "reports/confidence/confidence_summary.json": "capatch_policy.confidence",
    "reports/confidence/confidence_summary.md": "capatch_policy.confidence",
    "reports/telemetry/intervention_gates.json": "capatch_policy.intervention",
    "reports/telemetry/intervention_gates.md": "capatch_policy.intervention",
    "reports/findings/fix_execution.json": "fixer bridge",
    "reports/findings/fix_execution.md": "fixer bridge",
    "reports/verification/before_after_verification.json": "fixer bridge + verify",
    "reports/verification/before_after_verification.md": "fixer bridge + verify",
    "reports/patch_history/index.json": "capatch_audit.history",
}

for report_dir in REPORT_DIRS:
    if report_dir.endswith("patch_runs"):
        REPORT_FILE_OWNERS[f"{report_dir}/*"] = "capatch_audit.run_store"
    elif report_dir.endswith("checkpoints"):
        REPORT_FILE_OWNERS[f"{report_dir}/*"] = "capatch_fs.checkpoints"
    elif report_dir.endswith("rollback"):
        REPORT_FILE_OWNERS[f"{report_dir}/*"] = "capatch_audit.rollback_*"
    elif report_dir.endswith("baselines"):
        REPORT_FILE_OWNERS[f"{report_dir}/*"] = "capatch_audit.baseline_registry"
