from __future__ import annotations

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
