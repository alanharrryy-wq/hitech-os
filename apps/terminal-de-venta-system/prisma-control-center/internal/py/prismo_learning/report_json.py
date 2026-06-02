# PRISMO Learning Core V1.2 F3 fix1
# Generated package: prismo learn3 3005 1128 fix1
# Operation model: local, read-only runtime. Standard library only.

"""JSON report helpers.

Fix1: writes BOTH a latest deterministic report name and a timestamped snapshot.
This keeps endpoint status readers stable while preserving evidence history.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
from .atomic_io import atomic_write_json
from .paths import ensure_store
from .clock import sortable_stamp


def write_json_report(name: str, payload: dict[str, Any], base=None) -> Path:
    root = ensure_store(base) / "05_REPORTS"
    root.mkdir(parents=True, exist_ok=True)
    latest = root / f"{name}.json"
    atomic_write_json(latest, payload)
    stamped = root / f"{name}_{sortable_stamp()}.json"
    atomic_write_json(stamped, payload)
    return latest
