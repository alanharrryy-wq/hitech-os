from __future__ import annotations

from typing import Any

from .versions import CAPATCH_PLUGIN_RUNTIME_VERSION

ESSENTIAL_PLUGIN_IDS: tuple[str, ...] = (
    "fixer.safe-runtime-actions",
    "recommender.safe-fix-plan",
    "verifier.post-fix-verifier",
)

ESSENTIAL_PLUGIN_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "fixer.safe-runtime-actions": (
        "fix.apply.safe-runtime-actions",
        "lifecycle.transaction-aware",
    ),
    "recommender.safe-fix-plan": (
        "recommend.safe-fix-plan",
        "recommend.outputs.fix-proposal-v2",
    ),
    "verifier.post-fix-verifier": (
        "verify.post-fix",
        "verify.outputs.lifecycle-summary",
    ),
}

INFERRED_PLUGIN_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "fixer.safe-runtime-actions": (
        "fix.apply.safe-runtime-actions",
        "lifecycle.transaction-aware",
    ),
    "recommender.safe-fix-plan": (
        "recommend.safe-fix-plan",
        "recommend.outputs.fix-proposal-v2",
    ),
    "verifier.post-fix-verifier": (
        "verify.post-fix",
        "verify.outputs.lifecycle-summary",
    ),
}


def plugin_semver_tuple(value: str | None) -> tuple[int, int, int]:
    text = str(value or '').strip()
    raw = []
    for chunk in text.replace('-', '.').split('.'):
        if chunk.isdigit():
            raw.append(int(chunk))
        elif chunk:
            digits = ''.join(char for char in chunk if char.isdigit())
            if digits:
                raw.append(int(digits))
        if len(raw) >= 3:
            break
    while len(raw) < 3:
        raw.append(0)
    return raw[0], raw[1], raw[2]


def plugin_runtime_satisfies(min_runtime: str | None, runtime_version: str | None = None) -> bool:
    if not min_runtime:
        return True
    runtime_version = runtime_version or CAPATCH_PLUGIN_RUNTIME_VERSION
    return plugin_semver_tuple(runtime_version) >= plugin_semver_tuple(min_runtime)


def _dedupe(values: list[str] | tuple[str, ...] | None) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in list(values or []):
        token = str(value or '').strip()
        if not token or token in seen:
            continue
        seen.add(token)
        ordered.append(token)
    return ordered


def infer_plugin_capabilities(plugin_id: str, row: dict[str, Any] | None = None) -> list[str]:
    row = row if isinstance(row, dict) else {}
    manifest_caps = row.get('capabilities') if isinstance(row.get('capabilities'), (list, tuple)) else []
    registry_caps = row.get('declared_capabilities') if isinstance(row.get('declared_capabilities'), (list, tuple)) else []
    inferred = list(INFERRED_PLUGIN_CAPABILITIES.get(str(plugin_id or '').strip(), ()))
    return _dedupe(list(manifest_caps) + list(registry_caps) + inferred)


def _registry_row(registry: dict[str, Any] | None, plugin_id: str) -> dict[str, Any]:
    registry = registry if isinstance(registry, dict) else {}
    row = registry.get(plugin_id)
    return row if isinstance(row, dict) else {}


def summarize_essential_runtime_health(
    runtime_version: str | None,
    registry: dict[str, Any] | None,
    essential_plugin_ids: tuple[str, ...] = ESSENTIAL_PLUGIN_IDS,
    capability_map: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry if isinstance(registry, dict) else {}
    capability_map = capability_map if isinstance(capability_map, dict) else {}
    missing: list[str] = []
    rejected: list[str] = []
    disabled: list[str] = []
    duplicate: list[str] = []
    active: list[str] = []
    capability_status: dict[str, dict[str, Any]] = {}

    declared_by_plugin = capability_map.get('declared_capabilities_by_plugin') if isinstance(capability_map.get('declared_capabilities_by_plugin'), dict) else {}
    missing_caps_global: list[str] = []

    for plugin_id in essential_plugin_ids:
        row = _registry_row(registry, plugin_id)
        status = str(row.get('real_status') or row.get('status') or 'missing')
        if not row:
            missing.append(plugin_id)
        elif status == 'active':
            active.append(plugin_id)
        elif status == 'disabled':
            disabled.append(plugin_id)
        elif status == 'duplicate':
            duplicate.append(plugin_id)
        elif status == 'rejected':
            rejected.append(plugin_id)
        else:
            missing.append(plugin_id)

        declared_caps = declared_by_plugin.get(plugin_id) if isinstance(declared_by_plugin.get(plugin_id), list) else None
        inferred_caps = infer_plugin_capabilities(plugin_id, row)
        actual_caps = _dedupe(declared_caps if declared_caps is not None else inferred_caps)
        required_caps = list(ESSENTIAL_PLUGIN_CAPABILITIES.get(plugin_id, ()))
        missing_caps = [item for item in required_caps if item not in actual_caps]
        if missing_caps:
            missing_caps_global.extend(missing_caps)
        capability_status[plugin_id] = {
            'required': required_caps,
            'declared': actual_caps,
            'missing': missing_caps,
            'satisfied': not missing_caps,
        }

    severity = 'healthy'
    if missing or rejected or disabled:
        severity = 'failed'
    elif duplicate or missing_caps_global:
        severity = 'degraded'

    return {
        'status': severity,
        'runtime_version': runtime_version or CAPATCH_PLUGIN_RUNTIME_VERSION,
        'essential_plugin_ids': list(essential_plugin_ids),
        'active': active,
        'missing': missing,
        'rejected': rejected,
        'disabled': disabled,
        'duplicate': duplicate,
        'healthy': severity == 'healthy',
        'required_capabilities': {key: list(value) for key, value in ESSENTIAL_PLUGIN_CAPABILITIES.items()},
        'capability_status': capability_status,
        'missing_capabilities': _dedupe(missing_caps_global),
    }
