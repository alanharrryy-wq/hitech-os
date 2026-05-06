from __future__ import annotations

"""Canonical manifest for the homologated Ar-k registry builder governed handoff bundle."""

from pathlib import Path

TOP_LEVEL_DIR = "ark_registry_builder_bundle"
BUNDLE_ID = "registry_builder_bundle"
TOOL_ID = "registry_builder"
STATUS_READY = "READY FOR HANDOFF"
DEFAULT_INSTALL_REL = "bundles/registry_builder_bundle"
STATE_REL = ".ark_install/registry_builder_bundle"
ROLLBACK_STATE_REL = ".ark_install/registry_builder_bundle/last_apply.json"
BACKUPS_REL = ".ark_install/registry_builder_bundle/backups"
DEFAULT_LOG_DIR = r"F:\descargasf"
LOG_FILE_PREFIX = "Ar-k_registry_builder_int_"
CANONICAL_PORTABLE_INDEX_NAME = "registry_index.json"
LEGACY_INDEX_NAME = "query_index.json"
STAGE_ORDER = [
    "stage_01_scan",
    "stage_02_registry_build",
    "stage_03_switch_resolve",
    "stage_04_contract_validate",
    "stage_05_ai_annotate",
]
CANONICAL_OUTPUTS = [
    "module_registry.json",
    "boundary_registry.json",
    "registry_index.json",
]
BUILDER_LOCAL_OUTPUTS = [
    "registry_build_summary.json",
    "registry_bundle_snapshot.json",
    "registry_bundle_delta.json",
]
FORBIDDEN_WRITES = [
    "switch_decision_registry.json",
    "switch_decision_trace.json",
    "validation_report.json",
    "gate_decisions.json",
    "annotations.json",
    "annotation_index.json",
]
EXCLUSION_PATH_MARKERS = [
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
]
WRITER_OWNERSHIP = {
    "signals": "scanner",
    "module_registry": "registry_builder",
    "boundary_registry": "registry_builder",
    "registry_index": "registry_builder",
    "switch_decision_registry": "switch_engine",
    "switch_decision_trace": "switch_engine",
    "validation_report": "contract_validator",
    "gate_decisions": "contract_validator",
    "annotations": "ai_annotator",
    "annotation_index": "ai_annotator",
}
REQUIRED_ENTRYPOINTS = [
    "registry_builder_installer.py",
    "payload_manifest.py",
    "tools/validate_registry_builder_bundle.py",
    "tools/count_bundle_mix.py",
    "tools/generate_example_outputs.py",
    "contracts/module_registry_contract.py",
    "contracts/boundary_registry_contract.py",
    "contracts/registry_index_contract.py",
    "compat/query_index_alias.py",
    "policy/promotion_policy.py",
    "policy/write_limits.py",
    "policy/exclusions.py",
    "fixtures/catalog.py",
    "tests/test_contracts.py",
    "tests/test_installer_cli.py",
]


def bundle_root_from_here(here: str | Path) -> Path:
    candidate = Path(here).resolve()
    return candidate if candidate.name == TOP_LEVEL_DIR else candidate.parent
