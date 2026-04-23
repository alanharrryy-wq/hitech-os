from __future__ import annotations

import sys
import zipfile
from pathlib import Path

IGNORED_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ark_install"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def _keep_file(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    if any(part in IGNORED_DIRS for part in rel_parts):
        return False
    if path.suffix in IGNORED_SUFFIXES:
        return False
    return True


def inspect_directory(path: Path) -> dict[str, float | int | str]:
    files = [item for item in path.rglob("*") if item.is_file() and _keep_file(item, path)]
    py_count = sum(1 for item in files if item.suffix == ".py")
    return {
        "mode": "directory",
        "file_count": len(files),
        "py_count": py_count,
        "py_ratio": (py_count / len(files)) if files else 0.0,
        "compressed_size": 0,
    }


def inspect_zip(path: Path) -> dict[str, float | int | str]:
    with zipfile.ZipFile(path) as zf:
        names = [info.filename for info in zf.infolist() if not info.is_dir()]
    py_count = sum(1 for name in names if name.endswith(".py"))
    return {
        "mode": "zip",
        "file_count": len(names),
        "py_count": py_count,
        "py_ratio": (py_count / len(names)) if names else 0.0,
        "compressed_size": path.stat().st_size,
    }


def inspect_path(path: Path) -> dict[str, float | int | str]:
    if path.suffix == ".zip":
        return inspect_zip(path)
    return inspect_directory(path)


def main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    result = inspect_path(target)
    for key, value in result.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
