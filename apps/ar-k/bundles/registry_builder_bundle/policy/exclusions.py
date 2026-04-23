from __future__ import annotations

"""Executable exclusion rules with explicit coverage for reports_real/."""

from payload_manifest import EXCLUSION_PATH_MARKERS


def normalize_path(value: str) -> str:
    return value.replace('\\', '/').strip()


def is_excluded(path_value: str) -> bool:
    normalized = '/' + normalize_path(path_value).lstrip('/')
    return any(marker.strip('/') in normalized for marker in EXCLUSION_PATH_MARKERS)


def exclusion_examples() -> dict[str, bool]:
    samples = {
        'reports/output.json': True,
        'reports_real/registries/module_registry.json': True,
        '.ark_install/registry_builder_bundle/last_apply.json': True,
        'src/app/service.py': False,
        'node_modules/react/index.js': True,
        'build/generated/spec.py': True,
        'examples/sample_app/app.py': False,
    }
    return {path: is_excluded(path) for path in samples}
