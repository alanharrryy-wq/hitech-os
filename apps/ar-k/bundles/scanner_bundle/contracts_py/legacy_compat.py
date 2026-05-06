from __future__ import annotations

CANONICAL_INDEX_NAME = 'registry_index.json'
LEGACY_INDEX_NAME = 'query_index.json'

def canonicalize_index_name(name: str) -> tuple[str, bool]:
    normalized = name.strip()
    if normalized == LEGACY_INDEX_NAME:
        return CANONICAL_INDEX_NAME, True
    return normalized, False
