from __future__ import annotations

from pathlib import Path

LEGACY_DELETE_PATHS: tuple[str, ...] = (
    'shared/pyside6_glass/.pytest_cache',
    'shared/pyside6_glass/__pycache__',
    'shared/pyside6_glass/tests/__pycache__',
    'shared/pyside6_glass/examples/__pycache__',
    'shared/pyside6_glass/atlas_styles.py.bak_silver_case',
    'shared/pyside6_glass/atlas_theme_bridge.py.bak_silver_case',
    'shared/pyside6_glass/backdrop.py.bak_silver_case',
    'shared/pyside6_glass/theme.py.bak_silver_case',
    'shared/pyside6_glass/examples/catalog_shell.py.bak_silver_case',
    'shared/pyside6_glass/examples/demo_app.py.bak_silver_case',
)

LEGACY_REPLACE_PATHS: tuple[str, ...] = (
    'shared/pyside6_glass/README.md',
    'shared/pyside6_glass/ARCHITECTURE.md',
    'shared/pyside6_glass/INTEGRATION.md',
    'shared/pyside6_glass/backdrop.py',
    'shared/pyside6_glass/atlas_styles.py',
    'shared/pyside6_glass/atlas_theme_bridge.py',
    'shared/pyside6_glass/__init__.py',
)


def legacy_delete_paths() -> tuple[str, ...]:
    return LEGACY_DELETE_PATHS


def legacy_replace_paths() -> tuple[str, ...]:
    return LEGACY_REPLACE_PATHS


def should_delete_path(path: str | Path) -> bool:
    candidate = str(path).replace('\\', '/').rstrip('/')
    normalized = {item.rstrip('/') for item in LEGACY_DELETE_PATHS}
    return candidate in normalized


__all__ = [
    'LEGACY_DELETE_PATHS',
    'LEGACY_REPLACE_PATHS',
    'legacy_delete_paths',
    'legacy_replace_paths',
    'should_delete_path',
]
