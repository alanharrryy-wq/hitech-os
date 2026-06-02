# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Common JSON memory store with snapshots and atomic writes."""
from __future__ import annotations
import json, shutil
from pathlib import Path
from typing import Any
from .atomic_io import atomic_write_json, read_json
from .clock import sortable_stamp
from .locks import StoreLock
from .paths import ensure_store

STORE_FILES = {
    "semantic": "02_MEMORY/semantic_memory.json",
    "episodic": "02_MEMORY/episodic_memory.json",
    "procedural": "02_MEMORY/procedural_memory.json",
    "patterns": "03_PATTERNS/patterns.json",
    "protocol_stats": "04_PROTOCOL_STATS/protocol_stats.json",
    "authority": "02_MEMORY/authority.json",
}


def store_file(name: str, base: str | Path | None = None) -> Path:
    root = ensure_store(base)
    rel = STORE_FILES.get(name, f"02_MEMORY/{name}.json")
    return root / rel


def read_store(name: str, default: Any | None = None, base: str | Path | None = None) -> Any:
    if default is None:
        default = {"schema_version": "1.0.0", "records": []}
    return read_json(store_file(name, base), default)


def snapshot_store(name: str, base: str | Path | None = None) -> Path | None:
    path = store_file(name, base)
    if not path.exists():
        return None
    root = ensure_store(base)
    dest = root / "06_SNAPSHOTS" / f"{name}_{sortable_stamp()}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    return dest


def write_store(name: str, obj: Any, base: str | Path | None = None) -> Path:
    path = store_file(name, base)
    lock = path.with_suffix(path.suffix + ".lock")
    with StoreLock(lock):
        snapshot_store(name, base)
        atomic_write_json(path, obj)
    return path
