"""Registry I/O adapters that preserve read-only treatment of canonical inputs."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

from compat.canonical_index_shim import CanonicalIndexShim
from contracts.shared_canon import PORTABLE_CANONICAL_INDEX


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_canonical_inputs(registry_dir: Path) -> dict[str, object]:
    module_registry = registry_dir / "module_registry.json"
    boundary_registry = registry_dir / "boundary_registry.json"
    index_path, index_mode = CanonicalIndexShim(registry_dir).resolve()
    return {
        "module_registry": read_json(module_registry) if module_registry.exists() else [],
        "boundary_registry": read_json(boundary_registry) if boundary_registry.exists() else [],
        PORTABLE_CANONICAL_INDEX: read_json(index_path) if index_path.exists() else {},
        "index_resolution_mode": index_mode,
        "input_hashes": {
            "module_registry.json": hash_file(module_registry) if module_registry.exists() else None,
            "boundary_registry.json": hash_file(boundary_registry) if boundary_registry.exists() else None,
            index_path.name: hash_file(index_path) if index_path.exists() else None,
        },
    }
