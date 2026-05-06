from __future__ import annotations

import sys
import zipfile
from pathlib import Path

if __package__ in {None, ''}:
    bundle_root = Path(__file__).resolve().parents[1]
    if str(bundle_root) not in sys.path:
        sys.path.insert(0, str(bundle_root))

import payload_manifest
from contracts_py.report_sections import FINAL_REPORT_SECTIONS
from contracts_py.shared_canon import REQUIRED_TOP_LEVEL, STATE_REL, STATUS
from tools.count_bundle_mix import inspect_path


def validate_directory(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_TOP_LEVEL:
        if not (root / rel).exists():
            errors.append(f'missing:{rel}')
    report_path = root / 'FINAL_REPORT.md'
    if not report_path.exists():
        errors.append('missing:FINAL_REPORT.md')
        return errors
    report = report_path.read_text(encoding='utf-8')
    if f'1. STATUS\n{STATUS}' not in report:
        errors.append('status_mismatch')
    for section in FINAL_REPORT_SECTIONS:
        if section not in report:
            errors.append(f'missing_section:{section}')
    surface_count = len(payload_manifest.install_surface(root))
    if f'- Verification surface file count: {surface_count}' not in report:
        errors.append('verification_surface_count_mismatch')
    if f'- Verify outputs path: <root>/{STATE_REL}/verification_outputs/<timestamp>/' not in report:
        errors.append('verify_output_path_mismatch')
    return errors


def validate_zip(path: Path) -> list[str]:
    errors: list[str] = []
    with zipfile.ZipFile(path) as zf:
        names = [info.filename for info in zf.infolist() if not info.is_dir()]
    top_levels = {name.split('/', 1)[0] for name in names}
    if top_levels != {'ark_scanner_bundle'}:
        errors.append('top_level_dir_mismatch')
    return errors


def main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    errors = validate_zip(target) if target.suffix == '.zip' else validate_directory(target)
    stats = inspect_path(target)
    if stats['py_ratio'] < 0.90:
        errors.append('py_ratio_below_threshold')
    if target.suffix == '.zip' and stats['compressed_size'] < 307200:
        errors.append('zip_below_threshold')
    if errors:
        for item in errors:
            print(item)
        return 1
    print('validation=ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
