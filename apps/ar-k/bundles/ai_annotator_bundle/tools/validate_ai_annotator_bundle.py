from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

THIS_FILE = Path(__file__).resolve()
BUNDLE_ROOT = THIS_FILE.parents[1]
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

from core.bundle_constants import (
    ALLOWED_INSTALLER_FLAGS,
    DEFAULT_INSTALL_REL,
    DEFAULT_STATE_REL,
    FINAL_STATUS,
    LOG_FILENAME_PATTERN,
    TOP_LEVEL_DIR,
)
from core.report_sections import REPORT_SECTIONS
from tools.count_bundle_mix import inspect_directory, inspect_zip


REQUIRED_FILES = [
    'ai_annotator_installer.py',
    'payload_manifest.py',
    'tools/validate_ai_annotator_bundle.py',
    'tools/count_bundle_mix.py',
    'tools/generate_example_outputs.py',
    'FINAL_REPORT.md',
]


def load_installer(bundle_root: Path):
    installer_path = bundle_root / 'ai_annotator_installer.py'
    spec = importlib.util.spec_from_file_location('ai_annotator_installer', installer_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load installer: {installer_path}')
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(bundle_root))
    spec.loader.exec_module(module)
    return module


def _assert_mix_is_clean(mix: dict[str, object], *, context: str) -> None:
    if mix['dirty_entry_count']:
        raise RuntimeError(f"{context} contains dirty entries: {mix['dirty_entries']}")
    if mix['py_ratio'] < 0.9:
        raise RuntimeError(f"{context} python ratio below threshold: {mix['py_ratio']}")


def validate_bundle_dir(bundle_root: Path) -> dict[str, object]:
    missing = [item for item in REQUIRED_FILES if not (bundle_root / item).exists()]
    if missing:
        raise RuntimeError(f'Missing required files: {missing}')
    installer = load_installer(bundle_root)
    parser = installer.build_parser()
    option_names = sorted(
        action.option_strings[0]
        for action in parser._actions
        if action.option_strings
    )
    if option_names != sorted(ALLOWED_INSTALLER_FLAGS):
        raise RuntimeError(f'Installer option mismatch: {option_names}')
    if installer.DEFAULT_INSTALL_REL != DEFAULT_INSTALL_REL:
        raise RuntimeError('Default install path mismatch')
    if installer.DEFAULT_STATE_REL != DEFAULT_STATE_REL:
        raise RuntimeError('Default state path mismatch')
    if installer.LOG_FILENAME_PATTERN != LOG_FILENAME_PATTERN:
        raise RuntimeError('Log filename pattern mismatch')
    root_action = next(action for action in parser._actions if '--root' in action.option_strings)
    if not root_action.required:
        raise RuntimeError('Installer --root must be required')
    if root_action.default not in (None, argparse.SUPPRESS):
        raise RuntimeError(f'Installer --root must not have an implicit default: {root_action.default!r}')
    report = (bundle_root / 'FINAL_REPORT.md').read_text(encoding='utf-8')
    if FINAL_STATUS not in report:
        raise RuntimeError('Final status string mismatch')
    for section in REPORT_SECTIONS:
        if section not in report:
            raise RuntimeError(f'Missing report section: {section}')
    directory_mix = inspect_directory(bundle_root)
    _assert_mix_is_clean(directory_mix, context='Bundle directory')
    return {
        'bundle_root': str(bundle_root),
        'top_level_dir': TOP_LEVEL_DIR,
        'directory_mix': directory_mix,
        'status': 'ok',
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('target')
    ns = parser.parse_args()
    target = Path(ns.target)
    if target.suffix == '.zip':
        zip_mix = inspect_zip(target)
        if zip_mix['top_level_entries'] != [TOP_LEVEL_DIR]:
            raise RuntimeError(f"Unexpected zip top-level entries: {zip_mix['top_level_entries']}")
        if zip_mix['compressed_size_bytes'] < 307200:
            raise RuntimeError('ZIP compressed size below threshold')
        _assert_mix_is_clean(zip_mix, context='Shipped ZIP')
        print(json.dumps({'zip_mix': zip_mix}, indent=2))
        return 0
    result = validate_bundle_dir(target)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
