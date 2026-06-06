from __future__ import annotations

from pathlib import Path

from capatch_ops.base import CapatchError

from .guards import ensure_path_within_root


def resolve_target_path(base_dir: Path, relative_file: str) -> Path:
    relative = (relative_file or "").strip()
    if not relative:
        raise CapatchError("La operacion no trae file.")
    target = (base_dir / relative).resolve()
    ensure_path_within_root(base_dir, target)
    return target


def resolve_target_file(base_dir: Path, relative_file: str) -> Path:
    target = resolve_target_path(base_dir, relative_file)
    if not target.exists():
        raise CapatchError(f"No encontre el archivo objetivo: {target}")
    if not target.is_file():
        raise CapatchError(f"Se esperaba archivo, no carpeta: {target}")
    return target
