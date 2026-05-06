from __future__ import annotations

"""Executable write-limit policy for registry_builder."""

from payload_manifest import BUILDER_LOCAL_OUTPUTS, CANONICAL_OUTPUTS, FORBIDDEN_WRITES

ALLOWED_ARTIFACT_KEYS = {
    'module_registry',
    'boundary_registry',
    'registry_index',
    'registry_build_summary',
    'registry_bundle_snapshot',
    'registry_bundle_delta',
}


def normalized_allowed_outputs() -> list[str]:
    return sorted(set(CANONICAL_OUTPUTS + BUILDER_LOCAL_OUTPUTS))


def may_write_path(relative_path: str) -> bool:
    clean = relative_path.replace('\\', '/').lstrip('./')
    allowed = (
        clean.startswith('registries/module_registry')
        or clean.startswith('registries/boundary_registry')
        or clean.startswith('indices/registry_index')
        or clean.startswith('artifacts/metrics/registry_build_summary')
        or clean.startswith('snapshots/registry_bundle_')
        or clean.startswith('deltas/registry_bundle_')
    )
    forbidden = any(name in clean for name in FORBIDDEN_WRITES)
    return bool(allowed and not forbidden)


def forbidden_outputs() -> list[str]:
    return sorted(FORBIDDEN_WRITES)
