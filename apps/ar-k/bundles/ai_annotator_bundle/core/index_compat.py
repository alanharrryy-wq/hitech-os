"""Compatibility shim for legacy query_index naming.

Canon says registry_index.json is the only portable name. Some source snapshots
still reference query_index.json, so this shim performs a narrow translation
without resurrecting ambiguous dual-canon behavior.
"""

from __future__ import annotations

from pathlib import Path

from core.bundle_constants import CANONICAL_INDEX_NAME, LEGACY_INDEX_ALIAS


class IndexNameError(ValueError):
    """Raised when an index file name is unknown to the canon."""


def canonical_index_name(name: str) -> str:
    if name == CANONICAL_INDEX_NAME:
        return name
    if name == LEGACY_INDEX_ALIAS:
        return CANONICAL_INDEX_NAME
    raise IndexNameError(f"Unsupported index filename: {name}")


def canonical_index_path(path: str | Path) -> str:
    path = Path(path)
    if path.name == LEGACY_INDEX_ALIAS:
        return str(path.with_name(CANONICAL_INDEX_NAME)).replace("\\", "/")
    if path.name == CANONICAL_INDEX_NAME:
        return str(path).replace("\\", "/")
    raise IndexNameError(f"Unsupported index path: {path}")


def index_shim_report() -> dict[str, str]:
    return {
        "canonical": CANONICAL_INDEX_NAME,
        "legacy_alias": LEGACY_INDEX_ALIAS,
        "policy": "translate query_index.json to registry_index.json only at the compatibility boundary",
    }
