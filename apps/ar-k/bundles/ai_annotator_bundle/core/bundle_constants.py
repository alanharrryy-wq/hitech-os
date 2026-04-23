
"""Canonical constants for the homologated AI Annotator handoff bundle.

This module is the one true fruit stand for all bundle-level canon: layout,
paths, artifact names, stage order, index compatibility, exclusions, and log
naming. The installer, validators, tests, and example generators all depend on
these values so the bundle does not drift into five different neighborhood laws.
"""

from __future__ import annotations

TOP_LEVEL_DIR = "ark_ai_annotator_bundle"
BUNDLE_ID = "ai_annotator_bundle"
TOOL_ID = "ai_annotator"
SYSTEM_ID = "ar-k"
FINAL_STATUS = "READY FOR HANDOFF"

DEFAULT_INSTALL_REL = "bundles/ai_annotator_bundle"
DEFAULT_STATE_REL = ".ark_install/ai_annotator_bundle"
ROLLBACK_STATE_FILE = ".ark_install/ai_annotator_bundle/last_apply.json"
BACKUP_ROOT_REL = ".ark_install/ai_annotator_bundle/backups"
DEFAULT_LOG_DIR = r"F:\descargasf"
LOG_BASENAME_PREFIX = "Ar-k_ai_annotator_int_"
LOG_FILENAME_PATTERN = "Ar-k_ai_annotator_int_YYMMDD_HHMM.log"

CANONICAL_STAGE_ORDER = [
    "stage_01_scan",
    "stage_02_registry_build",
    "stage_03_switch_resolve",
    "stage_04_contract_validate",
    "stage_05_ai_annotate",
]

REQUIRED_ANNOTATION_ARTIFACTS = [
    "annotations.json",
    "annotation_index.json",
    "annotation_summary.json",
]

CANONICAL_INDEX_NAME = "registry_index.json"
LEGACY_INDEX_ALIAS = "query_index.json"

CANONICAL_REGISTRY_FILENAMES = [
    "module_registry.json",
    "boundary_registry.json",
    "registry_index.json",
    "switch_decision_registry.json",
    "switch_decision_trace.json",
    "validation_report.json",
    "gate_decisions.json",
    "annotations.json",
    "annotation_index.json",
]

EXCLUDED_RELATIVE_PREFIXES = [
    "reports/",
    "reports_real/",
    ".ark_install/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".venv/",
    "node_modules/",
    "dist/",
    "build/",
    "tmp/",
    "temp/",
    "runtime/",
    "generated/",
]

ADVISORY_OUTPUT_REL = "reports/annotations"
VERIFICATION_OUTPUT_REL = ".ark_install/ai_annotator_bundle/verification_outputs"

ALLOWED_INSTALLER_FLAGS = [
    "--dry-run",
    "--apply",
    "--verify",
    "--rollback",
    "--root",
    "--log-dir",
    "--install-rel",
]

FORBIDDEN_AUTHORITATIVE_WRITES = {
    "module_registry.json",
    "boundary_registry.json",
    "registry_index.json",
    "switch_decision_registry.json",
    "switch_decision_trace.json",
    "validation_report.json",
    "gate_decisions.json",
}

TOOL_INPUTS = [
    "module_registry.json",
    "boundary_registry.json",
    "registry_index.json",
    "switch_decision_registry.json",
    "switch_decision_trace.json",
    "validation_report.json",
    "gate_decisions.json",
]

TOOL_OUTPUTS = REQUIRED_ANNOTATION_ARTIFACTS[:]
