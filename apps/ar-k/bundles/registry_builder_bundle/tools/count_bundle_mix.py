from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile


def analyze_zip(zip_path: Path) -> dict:
    with ZipFile(zip_path, 'r') as zf:
        infos = [info for info in zf.infolist() if not info.is_dir()]
        py_entries = [info for info in infos if info.filename.endswith('.py')]
        non_py_entries = [info.filename for info in infos if not info.filename.endswith('.py')]
        top_level_roots = sorted({info.filename.split('/', 1)[0] for info in zf.infolist() if info.filename.strip('/')})
        return {
            'zip_path': str(zip_path),
            'compressed_size_bytes': sum(info.compress_size for info in infos),
            'entry_count': len(infos),
            'py_entry_count': len(py_entries),
            'non_py_entry_count': len(infos) - len(py_entries),
            'py_ratio': round((len(py_entries) / len(infos)) if infos else 0.0, 6),
            'non_py_entries': non_py_entries,
            'top_level_roots': top_level_roots,
            'top_level_root_count': len(top_level_roots),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description='Count Python-vs-non-Python mix in a bundle zip.')
    parser.add_argument('zip_path')
    args = parser.parse_args()
    result = analyze_zip(Path(args.zip_path))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
