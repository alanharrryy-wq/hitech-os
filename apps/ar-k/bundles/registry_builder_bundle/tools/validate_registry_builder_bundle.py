from __future__ import annotations

import argparse
import json
import subprocess
import sys
sys.dont_write_bytecode = True
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BUNDLE_ROOT = THIS_DIR.parent
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

from compat.query_index_alias import canonical_name, legacy_name, legacy_alias_metadata, resolve_requested_name
from payload_manifest import (
    DEFAULT_INSTALL_REL,
    REQUIRED_ENTRYPOINTS,
    ROLLBACK_STATE_REL,
    STATE_REL,
    STATUS_READY,
    TOP_LEVEL_DIR,
)

REQUIRED_REPORT_HEADERS = [
    '# 1. STATUS',
    '# 2. ROOT CAUSE / DRIFT REMOVED',
    '# 3. FILES CREATED / MODIFIED / DELETED',
    '# 4. COMMANDS RUN',
    '# 5. CANON ALIGNMENT',
    '# 6. VALIDATION RESULTS',
    '# 7. RISKS',
    '# 8. NEXT STEPS',
]
ALLOWED_DIRECTORY_ROOT_NAMES = {TOP_LEVEL_DIR, 'registry_builder_bundle'}


def validate_directory(bundle_root: Path) -> dict:
    files = [path for path in bundle_root.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    rel_files = sorted(str(path.relative_to(bundle_root)).replace('\\', '/') for path in files)
    missing = [item for item in REQUIRED_ENTRYPOINTS if item not in rel_files]
    non_py = [item for item in rel_files if not item.endswith('.py')]
    report_text = (bundle_root / 'FINAL_REPORT.md').read_text(encoding='utf-8')
    report_headers_ok = all(header in report_text for header in REQUIRED_REPORT_HEADERS)
    findings = {
        'bundle_root_name': bundle_root.name,
        'bundle_root_name_ok': bundle_root.name in ALLOWED_DIRECTORY_ROOT_NAMES,
        'required_missing': missing,
        'non_py_entries': non_py,
        'non_py_count': len(non_py),
        'py_count': len(rel_files) - len(non_py),
        'py_ratio': round(((len(rel_files) - len(non_py)) / len(rel_files)) if rel_files else 0.0, 6),
        'status_ready_present': STATUS_READY in report_text,
        'report_headers_ok': report_headers_ok,
        'canonical_index_name': canonical_name(),
        'legacy_index_name': legacy_name(),
        'legacy_alias_metadata': legacy_alias_metadata(),
        'legacy_name_resolves_to': resolve_requested_name(legacy_name()),
        'canonical_name_resolves_to': resolve_requested_name(canonical_name()),
        'install_rel_default': DEFAULT_INSTALL_REL,
        'state_rel': STATE_REL,
        'rollback_state_rel': ROLLBACK_STATE_REL,
        'root_required_in_installer': 'required=True' in (bundle_root / 'registry_builder_installer.py').read_text(encoding='utf-8'),
    }
    findings['ok'] = (
        findings['bundle_root_name_ok']
        and not missing
        and findings['status_ready_present']
        and findings['report_headers_ok']
        and findings['canonical_index_name'] == 'registry_index.json'
        and findings['legacy_index_name'] == 'query_index.json'
        and findings['legacy_name_resolves_to'] == 'registry_index.json'
        and findings['canonical_name_resolves_to'] == 'registry_index.json'
        and findings['py_ratio'] >= 0.90
        and findings['root_required_in_installer']
    )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate homologated registry builder bundle structure.')
    parser.add_argument('--bundle-root', default=str(BUNDLE_ROOT))
    parser.add_argument('--zip-path')
    args = parser.parse_args()
    result = validate_directory(Path(args.bundle_root).resolve())
    if args.zip_path:
        cmd = [sys.executable, str(BUNDLE_ROOT / 'tools' / 'count_bundle_mix.py'), args.zip_path]
        mix = json.loads(subprocess.check_output(cmd, text=True))
        result['zip_mix'] = mix
        zip_top_level_ok = mix['top_level_roots'] == [TOP_LEVEL_DIR]
        result['zip_top_level_ok'] = zip_top_level_ok
        result['ok'] = result['ok'] and mix['compressed_size_bytes'] >= 307200 and mix['py_ratio'] >= 0.90 and zip_top_level_ok
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
