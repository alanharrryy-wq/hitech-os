from __future__ import annotations

"""Executable policy proving observed-only scanner behavior and sole canonical writes for registry_builder."""

from collections import defaultdict
import hashlib
from typing import Iterable

from bundle_core.ownership import may_write

SCANNER_ALLOWED_WRITES = {"signals"}
REGISTRY_BUILDER_ALLOWED_WRITES = {
    "module_registry",
    "boundary_registry",
    "registry_index",
    "registry_build_summary",
    "registry_bundle_snapshot",
    "registry_bundle_delta",
}


def observed_only(signal: dict) -> bool:
    return signal.get("producer") == "scanner" and signal.get("state") in {"observed", "ambiguous", "candidate"}


def scanner_may_write(artifact_key: str) -> bool:
    return artifact_key in SCANNER_ALLOWED_WRITES


def registry_builder_may_write(artifact_key: str) -> bool:
    return artifact_key in REGISTRY_BUILDER_ALLOWED_WRITES or may_write("registry_builder", artifact_key)


def stable_id(prefix: str, *parts: str) -> str:
    joined = "|".join(parts)
    return f"{prefix}_{hashlib.sha256(joined.encode('utf-8')).hexdigest()[:16]}"


def _normalized_module_name(signal: dict) -> str:
    name = signal.get("module_name")
    if name:
        return str(name)
    source_path = str(signal["source_path"]).replace('\\', '/')
    return source_path[:-3].replace('/', '.') if source_path.endswith('.py') else source_path.replace('/', '.')


def _module_area(source_path: str, module_name: str) -> str:
    clean = source_path.replace('\\', '/')
    head = clean.split('/', 1)[0]
    return head or module_name.split('.', 1)[0]


def build_canonical_outputs(observed_signals: Iterable[dict], execution_id: str = 'verify_demo', execution_time: str = '2026-04-11T00:00:00Z') -> dict:
    grouped: dict[str, list[dict]] = defaultdict(list)
    import_edges: list[dict] = []
    boundaries: list[dict] = []
    for signal in observed_signals:
        signal_type = signal.get('signal_type')
        if signal_type == 'module_candidate':
            grouped[_normalized_module_name(signal)].append(signal)
        elif signal_type == 'import_edge':
            import_edges.append(signal)
        elif signal_type == 'boundary_candidate':
            boundaries.append(signal)
    module_registry: list[dict] = []
    module_lookup_by_name: dict[str, dict] = {}
    module_lookup_by_path: dict[str, dict] = {}
    for module_name in sorted(grouped):
        candidates = sorted(grouped[module_name], key=lambda item: item['source_path'])
        for idx, signal in enumerate(candidates):
            state = signal.get('state', 'observed')
            status = 'candidate' if state == 'ambiguous' else ('canonical' if idx == 0 else 'superseded')
            module_id = stable_id('mod', module_name, signal['source_path'])
            entry = {
                'module_id': module_id,
                'name': module_name,
                'kind': signal.get('kind', 'python_module'),
                'area': _module_area(signal['source_path'], module_name),
                'status': status,
                'source_of_truth': 'scanner.signals',
                'confidence': round(float(signal.get('confidence', 0.8)), 3),
                'declared_by': ['registry_builder'],
                'observed_in': [signal['source_path']],
                'tags': sorted(set(signal.get('tags', ['python', 'module']))),
                'boundaries': [],
                'switches': [f"module.enabled:{module_id}"],
                'updated_at': execution_time,
            }
            module_registry.append(entry)
            module_lookup_by_path[signal['source_path']] = entry
            if status == 'canonical':
                module_lookup_by_name[module_name] = entry
    boundary_registry: list[dict] = []
    for signal in sorted(import_edges, key=lambda item: (item['source_path'], item.get('target_import', ''))):
        source = module_lookup_by_path.get(signal['source_path'])
        if not source:
            continue
        imported = signal.get('target_import', '')
        target = module_lookup_by_name.get(imported)
        target_type = 'module' if target else 'external'
        target_id = target['module_id'] if target else f"external:{imported}"
        entry = {
            'boundary_id': stable_id('bnd', source['module_id'], imported, signal['source_path']),
            'source_module_id': source['module_id'],
            'target_id': target_id,
            'target_type': target_type,
            'boundary_type': 'import',
            'status': 'canonical',
            'source_of_truth': 'scanner.signals',
            'evidence': {'source_path': signal['source_path'], 'import': imported},
            'updated_at': execution_time,
        }
        source['boundaries'].append(entry['boundary_id'])
        boundary_registry.append(entry)
    for signal in sorted(boundaries, key=lambda item: (item['source_path'], item.get('boundary_kind', ''))):
        source = module_lookup_by_path.get(signal['source_path'])
        if not source:
            continue
        boundary_kind = signal.get('boundary_kind', 'observed_boundary')
        entry = {
            'boundary_id': stable_id('bnd', source['module_id'], boundary_kind, signal['source_path']),
            'source_module_id': source['module_id'],
            'target_id': f"capability:{boundary_kind}",
            'target_type': 'external',
            'boundary_type': boundary_kind,
            'status': 'canonical',
            'source_of_truth': 'scanner.signals',
            'evidence': {'source_path': signal['source_path'], 'boundary_kind': boundary_kind},
            'updated_at': execution_time,
        }
        source['boundaries'].append(entry['boundary_id'])
        boundary_registry.append(entry)
    for module in module_registry:
        module['boundaries'] = sorted(module['boundaries'])
    registry_index: list[dict] = []
    for module in sorted(module_registry, key=lambda item: item['module_id']):
        registry_index.append({
            'index_id': stable_id('idx', 'module', module['module_id']),
            'entity_type': 'module',
            'entity_id': module['module_id'],
            'lookup_keys': sorted(set([module['name'], module['module_id'], *module['observed_in'], *module.get('tags', [])])),
            'registry_source': 'module_registry',
            'snapshot_id': execution_id,
            'updated_at': execution_time,
        })
    for boundary in sorted(boundary_registry, key=lambda item: item['boundary_id']):
        registry_index.append({
            'index_id': stable_id('idx', 'boundary', boundary['boundary_id']),
            'entity_type': 'boundary',
            'entity_id': boundary['boundary_id'],
            'lookup_keys': sorted(set([boundary['boundary_type'], boundary['source_module_id'], boundary['target_id']])),
            'registry_source': 'boundary_registry',
            'snapshot_id': execution_id,
            'updated_at': execution_time,
        })
    return {
        'module_registry': module_registry,
        'boundary_registry': boundary_registry,
        'registry_index': registry_index,
    }
