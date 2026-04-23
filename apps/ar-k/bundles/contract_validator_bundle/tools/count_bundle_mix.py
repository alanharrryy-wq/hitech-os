
from __future__ import annotations

import json
import zipfile
from pathlib import Path


def inspect_zip(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path, 'r') as zf:
        infos = [info for info in zf.infolist() if not info.is_dir()]
        py_files = [info for info in infos if info.filename.endswith('.py')]
        return {
            'zip_path': str(zip_path),
            'compressed_size': zip_path.stat().st_size,
            'entry_count': len(infos),
            'py_entry_count': len(py_files),
            'py_ratio': round((len(py_files) / len(infos)) if infos else 0.0, 6),
            'non_py_entries': sorted([info.filename for info in infos if not info.filename.endswith('.py')]),
        }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--zip-path', required=True)
    args = parser.parse_args()
    print(json.dumps(inspect_zip(Path(args.zip_path)), indent=2, sort_keys=True))
