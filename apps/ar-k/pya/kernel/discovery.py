from __future__ import annotations

import json
import os
from pathlib import Path

from pya.kernel.identity import path_is_within_root

SKIP_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".pnpm",
    "dist",
    "build",
    "coverage",
    ".next",
    ".turbo",
}


def discover_engine_manifests(root: Path) -> list[Path]:
    engine_root = root / "pya" / "engines"
    return sorted(engine_root.glob("*/manifest.json"))


def load_json_file(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_files_with_stats(target: Path) -> tuple[list[Path], dict[str, int]]:
    target = target.resolve()
    files: list[Path] = []
    skipped_vendor_dir_count = 0
    skipped_external_path_count = 0

    for dirpath, dirnames, filenames in os.walk(target, topdown=True, followlinks=False):
        kept_dirnames: list[str] = []
        for dirname in dirnames:
            if dirname in SKIP_DIR_NAMES:
                skipped_vendor_dir_count += 1
                continue
            kept_dirnames.append(dirname)
        dirnames[:] = kept_dirnames

        current_dir = Path(dirpath)
        for filename in filenames:
            path = current_dir / filename
            if not path_is_within_root(path, target):
                skipped_external_path_count += 1
                continue
            files.append(path)

    return sorted(files), {
        "skipped_vendor_dir_count": skipped_vendor_dir_count,
        "skipped_external_path_count": skipped_external_path_count,
    }


def discover_files(target: Path) -> list[Path]:
    files, _ = discover_files_with_stats(target)
    return files
