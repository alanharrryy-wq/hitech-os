from __future__ import annotations

STATUS = 'READY FOR HANDOFF'
STAGES = ('stage_01_scan', 'stage_02_registry_build', 'stage_03_switch_resolve', 'stage_04_contract_validate', 'stage_05_ai_annotate')
EXCLUDED_SEGMENTS = ('reports', 'reports_real', '.ark_install', '__pycache__', '.pytest_cache', '.mypy_cache', '.venv', 'node_modules', 'dist', 'build', 'tmp', 'temp', 'runtime', 'generated')
DEFAULT_INSTALL_REL = 'bundles/scanner_bundle'
STATE_REL = '.ark_install/scanner_bundle'
LAST_APPLY_REL = '.ark_install/scanner_bundle/last_apply.json'
LOG_DIR_DEFAULT = r'F:\descargasf'
LOG_FILE_PREFIX = 'Ar-k_scanner_int_'
CANONICAL_INDEX_NAME = 'registry_index.json'
LEGACY_INDEX_NAME = 'query_index.json'
FINAL_REPORT_SECTIONS = (
    '1. STATUS',
    '2. ROOT CAUSE',
    '3. FILES CREATED / MODIFIED / DELETED',
    '4. COMMANDS RUN',
    '5. HOMOLOGATION FIX',
    '6. VALIDATION RESULTS',
    '7. RISKS',
    '8. NEXT STEPS',
)
REQUIRED_TOP_LEVEL = (
    'README.md',
    'FINAL_REPORT.md',
    'scanner_installer.py',
    'payload_manifest.py',
    'tools/validate_scanner_bundle.py',
    'tools/count_bundle_mix.py',
    'tools/generate_example_outputs.py',
    'contracts_py',
    'fixtures_py',
    'tests',
    'payload/bundles/scanner_bundle',
)
