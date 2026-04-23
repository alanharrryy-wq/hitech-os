"""Structural validator for the homologated switch bundle."""

from __future__ import annotations

import sys
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

import argparse
import json
import os
from zipfile import ZipFile

from contracts.exclusion_policy import should_exclude
from contracts.shared_canon import (
    DEFAULT_INSTALL_REL,
    LAST_APPLY_REL,
    PORTABLE_CANONICAL_INDEX,
    REQUIRED_SWITCH_ARTIFACTS,
    STATE_REL,
    TOP_LEVEL_DIR,
    FINAL_STATUS,
    is_canonical_bundle_root_name,
)

REQUIRED_FILES = [
    'switch_engine_installer.py',
    'payload_manifest.py',
    'tools/validate_switch_engine_bundle.py',
    'tools/count_bundle_mix.py',
    'tools/generate_example_outputs.py',
    'FINAL_REPORT.md',
    'compat/canonical_index_shim.py',
    'contracts/shared_canon.py',
    'contracts/artifact_contracts.py',
    'switch_engine/resolver.py',
]


def validate_tree(bundle_root: Path) -> dict[str, object]:
    missing = [rel for rel in REQUIRED_FILES if not (bundle_root / rel).exists()]
    report = {
        'bundle_root': str(bundle_root),
        'missing': missing,
        'top_level_name_ok': is_canonical_bundle_root_name(bundle_root.name),
        'reports_real_excluded': should_exclude('apps/ar-k/reports_real/example.json'),
        'install_rel': str(DEFAULT_INSTALL_REL),
        'state_rel': str(STATE_REL),
        'rollback_rel': str(LAST_APPLY_REL),
        'canonical_index_name': PORTABLE_CANONICAL_INDEX,
        'required_artifacts': list(REQUIRED_SWITCH_ARTIFACTS),
        'final_status_expected': FINAL_STATUS,
    }
    report['ok'] = not missing and report['top_level_name_ok'] and report['reports_real_excluded']
    return report


def validate_zip(zip_path: Path) -> dict[str, object]:
    with ZipFile(zip_path) as zf:
        names = [info.filename for info in zf.infolist() if not info.is_dir()]
    top_level_roots = sorted({Path(name).parts[0] for name in names})
    return {
        'zip_path': str(zip_path),
        'top_level_roots': top_level_roots,
        'one_top_level_root': top_level_roots == [TOP_LEVEL_DIR],
        'contains_final_report': f'{TOP_LEVEL_DIR}/FINAL_REPORT.md' in names,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Validate switch bundle structure')
    parser.add_argument('--bundle-root', required=True)
    parser.add_argument('--zip-path')
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = {'tree': validate_tree(Path(args.bundle_root).resolve())}
    if args.zip_path:
        payload['zip'] = validate_zip(Path(args.zip_path).resolve())
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload['tree']['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
