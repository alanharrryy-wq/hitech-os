"""Shared canon used by the homologated Ar-k handoff bundles.

This module is intentionally Python-first so the bundle remains script-heavy while
still carrying explicit governance. The constants here define the path, naming,
stage-order, and reporting canon that the switch bundle must follow.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

FINAL_STATUS = "READY FOR HANDOFF"
TOP_LEVEL_DIR = "ark_switch_engine_bundle"
DEFAULT_INSTALL_REL = PurePosixPath("bundles/switch_engine_bundle")
INSTALLED_BUNDLE_DIRNAME = DEFAULT_INSTALL_REL.name
STATE_REL = PurePosixPath(".ark_install/switch_engine_bundle")
LAST_APPLY_REL = STATE_REL / "last_apply.json"
BACKUP_REL = STATE_REL / "backups"
DEFAULT_LOG_DIR = r"F:\descargasf"
LOG_BASENAME_PREFIX = "Ar-k_switch_engine_int_"
PORTABLE_CANONICAL_INDEX = "registry_index.json"
LEGACY_INDEX_NAME = "query_index.json"
STAGE_ORDER = [
    "stage_01_scan",
    "stage_02_registry_build",
    "stage_03_switch_resolve",
    "stage_04_contract_validate",
    "stage_05_ai_annotate",
]
REQUIRED_SWITCH_ARTIFACTS = [
    "switch_decision_registry.json",
    "switch_decision_trace.json",
    "switch_resolution_summary.json",
]
EXCLUDED_PARTS = {
    "reports",
    "reports_real",
    ".ark_install",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "tmp",
    "temp",
    "runtime",
    "generated",
}
READ_ONLY_INPUTS = {
    "module_registry.json",
    "boundary_registry.json",
    PORTABLE_CANONICAL_INDEX,
    LEGACY_INDEX_NAME,
}
FORBIDDEN_WRITES = {
    "module_registry.json",
    "boundary_registry.json",
    PORTABLE_CANONICAL_INDEX,
    LEGACY_INDEX_NAME,
    "scan_observed_modules.json",
    "scan_observed_boundaries.json",
    "scan_observed_paths.json",
    "scan_observed_summary.json",
    "validation_report.json",
    "gate_decisions.json",
    "validator_summary.json",
    "annotations.json",
    "annotation_index.json",
    "annotation_summary.json",
}


@dataclass(frozen=True)
class CanonSummary:
    final_status: str = FINAL_STATUS
    top_level_dir: str = TOP_LEVEL_DIR
    default_install_rel: str = str(DEFAULT_INSTALL_REL)
    state_rel: str = str(STATE_REL)
    rollback_state_rel: str = str(LAST_APPLY_REL)
    backup_rel: str = str(BACKUP_REL)
    default_log_dir: str = DEFAULT_LOG_DIR
    canonical_index_name: str = PORTABLE_CANONICAL_INDEX
    legacy_index_name: str = LEGACY_INDEX_NAME


def as_dict() -> dict[str, object]:
    return {
        "final_status": FINAL_STATUS,
        "top_level_dir": TOP_LEVEL_DIR,
        "default_install_rel": str(DEFAULT_INSTALL_REL),
        "state_rel": str(STATE_REL),
        "rollback_state_rel": str(LAST_APPLY_REL),
        "backup_rel": str(BACKUP_REL),
        "default_log_dir": DEFAULT_LOG_DIR,
        "canonical_index_name": PORTABLE_CANONICAL_INDEX,
        "legacy_index_name": LEGACY_INDEX_NAME,
        "stage_order": list(STAGE_ORDER),
        "required_switch_artifacts": list(REQUIRED_SWITCH_ARTIFACTS),
        "excluded_parts": sorted(EXCLUDED_PARTS),
    }


def canonical_bundle_root_names() -> tuple[str, str]:
    return TOP_LEVEL_DIR, INSTALLED_BUNDLE_DIRNAME


def is_canonical_bundle_root_name(name: str) -> bool:
    return name in canonical_bundle_root_names()
