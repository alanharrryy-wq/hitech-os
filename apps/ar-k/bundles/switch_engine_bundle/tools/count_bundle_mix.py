"""Count bundle composition and prove Python-heavy economics."""

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


def count_tree(root: Path) -> dict[str, object]:
    files = [path for path in root.rglob('*') if path.is_file()]
    py_files = [path for path in files if path.suffix == '.py']
    ratio = (len(py_files) / len(files)) if files else 0.0
    return {
        'mode': 'tree',
        'root': str(root),
        'file_count': len(files),
        'py_count': len(py_files),
        'py_ratio': ratio,
        'non_py': sorted(str(path.relative_to(root)) for path in files if path.suffix != '.py'),
    }


def count_zip(zip_path: Path) -> dict[str, object]:
    with ZipFile(zip_path) as zf:
        infos = [info for info in zf.infolist() if not info.is_dir()]
        py_infos = [info for info in infos if Path(info.filename).suffix == '.py']
        ratio = (len(py_infos) / len(infos)) if infos else 0.0
        return {
            'mode': 'zip',
            'zip_path': str(zip_path),
            'compressed_size_bytes': os.path.getsize(zip_path),
            'file_count': len(infos),
            'py_count': len(py_infos),
            'py_ratio': ratio,
            'non_py': sorted(info.filename for info in infos if Path(info.filename).suffix != '.py'),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Count bundle Python mix and zip size')
    parser.add_argument('--root', help='Bundle root directory')
    parser.add_argument('--zip', dest='zip_path', help='ZIP file to inspect')
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.root:
        payload = count_tree(Path(args.root).resolve())
    elif args.zip_path:
        payload = count_zip(Path(args.zip_path).resolve())
    else:
        raise SystemExit('Provide --root or --zip')
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
