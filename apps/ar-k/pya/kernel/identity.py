from __future__ import annotations

from pathlib import Path

from pya.contracts.base import deterministic_id, stable_hash


def path_is_within_root(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except Exception:
        return False


def normalize_relpath(path: Path, base: Path) -> str:
    resolved_path = path.resolve()
    resolved_base = base.resolve()
    try:
        return resolved_path.relative_to(resolved_base).as_posix()
    except ValueError as exc:
        raise ValueError(f"path escapes target root: path={resolved_path} base={resolved_base}") from exc


def module_id_from_path(path: str) -> str:
    return deterministic_id("mod", path.lower())


def snapshot_id_from_payload(family: str, payload: object) -> str:
    return deterministic_id("snp", family, stable_hash(payload))
