from __future__ import annotations

from pathlib import Path

from pya.contracts.base import deterministic_id, stable_hash


def normalize_relpath(path: Path, base: Path) -> str:
    return path.resolve().relative_to(base.resolve()).as_posix()


def module_id_from_path(path: str) -> str:
    return deterministic_id("mod", path.lower())


def snapshot_id_from_payload(family: str, payload: object) -> str:
    return deterministic_id("snp", family, stable_hash(payload))
