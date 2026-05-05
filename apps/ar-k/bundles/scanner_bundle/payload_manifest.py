from __future__ import annotations

from pathlib import Path

DEFAULT_INSTALL_REL = "bundles/scanner_bundle"
STATE_REL = ".ark_install/scanner_bundle"
LAST_APPLY_REL = ".ark_install/scanner_bundle/last_apply.json"
IGNORED_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ark_install"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def keep_relative_path(rel_path: Path) -> bool:
    return not any(part in IGNORED_DIRS for part in rel_path.parts) and rel_path.suffix not in IGNORED_SUFFIXES


def install_surface(bundle_root: Path | None = None) -> list[str]:
    root = Path(bundle_root) if bundle_root is not None else Path(__file__).resolve().parent
    files: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if not keep_relative_path(rel):
            continue
        files.append(rel.as_posix())
    return sorted(files)


PAYLOAD_FILES = install_surface()
