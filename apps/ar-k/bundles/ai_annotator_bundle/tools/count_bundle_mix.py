from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path, PurePosixPath

DIRTY_DIR_NAMES = {'__pycache__', '.pytest_cache', '.mypy_cache'}
DIRTY_SUFFIXES = {'.pyc', '.pyo'}
DIRTY_PREFIXES = (
    '__pycache__/',
    '.pytest_cache/',
    '.mypy_cache/',
    '.ark_install/',
    'dist/',
    'build/',
    'tmp/',
    'temp/',
    'runtime/',
    'generated/',
)


def _is_dirty_posix(rel_posix: str) -> bool:
    pure = PurePosixPath(rel_posix)
    if any(part in DIRTY_DIR_NAMES for part in pure.parts):
        return True
    if pure.suffix in DIRTY_SUFFIXES:
        return True
    return rel_posix.startswith(DIRTY_PREFIXES)


def inspect_directory(root: Path) -> dict[str, object]:
    files: list[Path] = []
    dirty_entries: list[str] = []
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        files.append(path)
        if _is_dirty_posix(rel):
            dirty_entries.append(rel)
    py_files = [path for path in files if path.suffix == '.py']
    return {
        'mode': 'directory',
        'path': str(root),
        'file_count': len(files),
        'py_count': len(py_files),
        'non_py_count': len(files) - len(py_files),
        'py_ratio': round((len(py_files) / len(files)) if files else 0.0, 6),
        'compressed_size_bytes': None,
        'dirty_entry_count': len(dirty_entries),
        'dirty_entries': dirty_entries,
        'top_level_entries': sorted({item.relative_to(root).parts[0] for item in files}),
    }


def inspect_zip(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path) as zf:
        entries = [info for info in zf.infolist() if not info.is_dir()]
        dirty_entries = [info.filename for info in entries if _is_dirty_posix(info.filename)]
        py_entries = [info for info in entries if info.filename.endswith('.py')]
        return {
            'mode': 'zip',
            'path': str(path),
            'file_count': len(entries),
            'py_count': len(py_entries),
            'non_py_count': len(entries) - len(py_entries),
            'py_ratio': round((len(py_entries) / len(entries)) if entries else 0.0, 6),
            'compressed_size_bytes': path.stat().st_size,
            'dirty_entry_count': len(dirty_entries),
            'dirty_entries': dirty_entries,
            'top_level_entries': sorted({item.filename.split('/')[0] for item in entries}),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('target')
    ns = parser.parse_args()
    target = Path(ns.target)
    data = inspect_zip(target) if target.suffix == '.zip' else inspect_directory(target)
    print(json.dumps(data, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
