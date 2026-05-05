from __future__ import annotations

"""Explicit legacy compatibility shim mapping query_index.json callers to registry_index.json."""

from payload_manifest import CANONICAL_PORTABLE_INDEX_NAME, LEGACY_INDEX_NAME

MIGRATION_NOTE = (
    'Legacy runtime callers may request query_index.json. '
    'The portable canonical artifact remains registry_index.json; '
    'this shim presents an alias view without renaming or duplicating the source of truth.'
)


def canonical_name() -> str:
    return CANONICAL_PORTABLE_INDEX_NAME


def legacy_name() -> str:
    return LEGACY_INDEX_NAME


def resolve_requested_name(requested_name: str) -> str:
    clean = requested_name.strip()
    if clean == CANONICAL_PORTABLE_INDEX_NAME:
        return CANONICAL_PORTABLE_INDEX_NAME
    if clean == LEGACY_INDEX_NAME:
        return CANONICAL_PORTABLE_INDEX_NAME
    raise ValueError(f'unsupported index request: {requested_name}')


def legacy_alias_metadata() -> dict[str, str]:
    return {
        'requested_name': LEGACY_INDEX_NAME,
        'canonical_source': CANONICAL_PORTABLE_INDEX_NAME,
        'authoritative': 'false',
        'migration_note': MIGRATION_NOTE,
    }


def adapt_registry_index_for_legacy(registry_index_entries: list[dict]) -> dict:
    payload = legacy_alias_metadata()
    payload['entries'] = list(registry_index_entries)
    return payload
