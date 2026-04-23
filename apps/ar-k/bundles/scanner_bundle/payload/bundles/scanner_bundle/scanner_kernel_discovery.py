from __future__ import annotations

import os
from pathlib import Path

SKIP_DIR_NAMES = {
    '.git',
    '__pycache__',
    '.venv',
    'venv',
    'node_modules',
    '.pnpm',
    'dist',
    'build',
    'coverage',
    '.next',
    '.turbo',
    'tmp',
    'temp',
    'runtime',
    'generated',
    '.ark_install',
    '.pytest_cache',
    '.mypy_cache',
    'reports',
    'reports_real',
}


def discover_files_with_stats(target: Path) -> tuple[list[Path], dict[str, int]]:
    target = target.resolve()
    files: list[Path] = []
    skipped_vendor_dir_count = 0
    skipped_external_path_count = 0
    for dirpath, dirnames, filenames in os.walk(target, topdown=True, followlinks=False):
        kept: list[str] = []
        for dirname in dirnames:
            if dirname in SKIP_DIR_NAMES:
                skipped_vendor_dir_count += 1
                continue
            kept.append(dirname)
        dirnames[:] = kept
        current = Path(dirpath)
        for filename in filenames:
            path = current / filename
            try:
                resolved = path.resolve()
            except FileNotFoundError:
                skipped_external_path_count += 1
                continue
            if target not in resolved.parents and resolved != target:
                skipped_external_path_count += 1
                continue
            files.append(path)
    return sorted(files), {
        'skipped_vendor_dir_count': skipped_vendor_dir_count,
        'skipped_external_path_count': skipped_external_path_count,
    }
