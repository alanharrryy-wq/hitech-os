# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Store manifest helpers."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from .atomic_io import atomic_write_json, read_json
from .clock import now_iso
from .paths import ensure_store


def load_store_manifest(base=None) -> dict[str, Any]:
    root = ensure_store(base)
    return read_json(root / "store_manifest.json", {"schema_version": "1.0.0", "created_at": now_iso()})


def update_store_manifest(patch: dict[str, Any], base=None) -> dict[str, Any]:
    root = ensure_store(base)
    manifest = load_store_manifest(base)
    manifest.update(patch)
    manifest["updated_at"] = now_iso()
    atomic_write_json(root / "store_manifest.json", manifest)
    return manifest
