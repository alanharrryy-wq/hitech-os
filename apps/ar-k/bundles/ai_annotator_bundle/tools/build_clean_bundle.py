from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True

THIS_FILE = Path(__file__).resolve()
BUNDLE_ROOT = THIS_FILE.parents[1]
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))
from core.bundle_constants import TOP_LEVEL_DIR

TOP_LEVEL_NAME = TOP_LEVEL_DIR
from tools.count_bundle_mix import _is_dirty_posix
from tools.validate_ai_annotator_bundle import validate_bundle_dir


def iter_clean_files(root: Path):
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if _is_dirty_posix(rel):
            continue
        yield path, rel


def build_zip(output_zip: Path) -> Path:
    validate_bundle_dir(BUNDLE_ROOT)
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()
    with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path, rel in iter_clean_files(BUNDLE_ROOT):
            zf.write(path, arcname=f'{TOP_LEVEL_NAME}/{rel}')
    return output_zip


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('output_zip')
    ns = parser.parse_args()
    output = build_zip(Path(ns.output_zip).resolve())
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
