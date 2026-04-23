from __future__ import annotations

from pathlib import Path

SHARED_STAGE_ORDER = ['stage_01_scan', 'stage_02_registry_build', 'stage_03_switch_resolve', 'stage_04_contract_validate', 'stage_05_ai_annotate']
FINAL_STATUS_WORDING = 'READY FOR HANDOFF'
ARCHIVE_TOP_LEVEL_DIR = 'ark_contract_validator_bundle'
INSTALLED_BUNDLE_DIRNAME = 'contract_validator_bundle'
TOP_LEVEL_DIR = ARCHIVE_TOP_LEVEL_DIR
INSTALL_REL_DEFAULT = f'bundles/{INSTALLED_BUNDLE_DIRNAME}'
STATE_ROOT_REL = '.ark_install/contract_validator_bundle'
STATE_FILE = '.ark_install/contract_validator_bundle/last_apply.json'
BACKUP_ROOT_REL = '.ark_install/contract_validator_bundle/backups'
PORTABLE_INDEX_NAME = 'registry_index.json'
QUERY_INDEX_COMPAT_ALIAS = 'query_index.json'
REQUIRED_VALIDATOR_ARTIFACTS = [
    'validation_report.json',
    'gate_decisions.json',
    'validator_summary.json',
]
EXCLUDED_PATH_PARTS = [
    'reports',
    'reports_real',
    '.ark_install',
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.venv',
    'node_modules',
    'dist',
    'build',
    'tmp',
    'temp',
    'runtime_output',
]
SINGLE_WRITER = {
    'signals': 'scanner',
    'module_registry': 'registry_builder',
    'boundary_registry': 'registry_builder',
    'registry_index': 'registry_builder',
    'switch_decision_registry': 'switch_engine',
    'switch_decision_trace': 'switch_engine',
    'validation_report': 'contract_validator',
    'gate_decisions': 'contract_validator',
    'validator_summary': 'contract_validator',
    'annotations': 'ai_annotator',
    'annotation_index': 'ai_annotator',
}


def canonical_bundle_root_names() -> tuple[str, str]:
    return ARCHIVE_TOP_LEVEL_DIR, INSTALLED_BUNDLE_DIRNAME


def is_canonical_bundle_root_name(name: str) -> bool:
    return name in canonical_bundle_root_names()


def bundle_root_role(bundle_root: Path | str) -> str:
    name = bundle_root.name if isinstance(bundle_root, Path) else str(bundle_root)
    if name == ARCHIVE_TOP_LEVEL_DIR:
        return 'archive_top_level'
    if name == INSTALLED_BUNDLE_DIRNAME:
        return 'installed_subtree'
    return 'unknown'


def canonical_bundle_mapping() -> dict[str, str | list[str]]:
    return {
        'archive_top_level_dir': ARCHIVE_TOP_LEVEL_DIR,
        'installed_subtree_name': INSTALLED_BUNDLE_DIRNAME,
        'accepted_bundle_root_names': list(canonical_bundle_root_names()),
        'install_rel_default': INSTALL_REL_DEFAULT,
        'state_root_rel': STATE_ROOT_REL,
        'state_file': STATE_FILE,
        'backup_root_rel': BACKUP_ROOT_REL,
    }
