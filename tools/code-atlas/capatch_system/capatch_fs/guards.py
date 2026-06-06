from __future__ import annotations

import os
from pathlib import Path

from capatch_ops.base import CapatchError


def fail(message: str) -> None:
    raise CapatchError(message)


def ensure_path_within_root(root_dir: Path, path_value: Path) -> None:
    root_resolved = root_dir.resolve()
    path_resolved = path_value.resolve()
    try:
        path_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise CapatchError(
            f"La ruta objetivo se sale de root_dir: {path_resolved} (root_dir: {root_resolved})"
        ) from exc


def ensure_directory(path_value: Path) -> None:
    if not path_value.exists():
        fail(f"No existe la ruta: {path_value}")
    if not path_value.is_dir():
        fail(f"La ruta no es carpeta: {path_value}")


def _is_windows_reparse_point(path_value: Path) -> bool:
    if os.name != "nt":
        return False
    try:
        return bool(getattr(path_value.lstat(), "st_file_attributes", 0) & 0x400)
    except Exception:
        return False


def ensure_not_linked_path(path_value: Path) -> None:
    if path_value.is_symlink() or _is_windows_reparse_point(path_value):
        fail(f"Se rechaza ruta enlazada/reparse point: {path_value}")


def ensure_safe_path_components(root_dir: Path, path_value: Path) -> None:
    root_resolved = Path(root_dir).resolve()
    target = Path(path_value)
    parts: list[Path] = []
    current = target if target.exists() else target.parent
    while True:
        parts.append(current)
        if current == root_resolved:
            break
        if current.parent == current:
            break
        current = current.parent
    for candidate in reversed(parts):
        ensure_path_within_root(root_resolved, candidate)
        if candidate.exists():
            ensure_not_linked_path(candidate)


def ensure_mutable_target(root_dir: Path, path_value: Path, *, allow_missing: bool = True) -> Path:
    root_resolved = Path(root_dir).resolve()
    path_value = Path(path_value)
    if not path_value.is_absolute():
        path_value = root_resolved / path_value
    ensure_path_within_root(root_resolved, path_value)
    if path_value.exists():
        ensure_not_linked_path(path_value)
    elif not allow_missing:
        fail(f"No existe la ruta objetivo: {path_value}")
    ensure_safe_path_components(root_resolved, path_value)
    return path_value.resolve(strict=False)
