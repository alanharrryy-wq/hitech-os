from __future__ import annotations

from pathlib import Path


def detect_surface_for_path(path_value: str) -> set[str]:
    value = str(path_value).replace('\\', '/').lower()
    surfaces: set[str] = set()
    if value.startswith('products/tablet/'):
        surfaces.add('prisma-tablet')
    if value.startswith('products/pc/'):
        surfaces.add('prisma-pc')
    if value.startswith('products/mobile/'):
        surfaces.add('prisma-mobile')
    if value.endswith(('.tsx', '.jsx')) or '/components/' in value or '/app/' in value:
        surfaces.add('react-ui')
    if value.endswith(('.css', '.module.css', '.scss', '.tsx', '.jsx')):
        surfaces.add('visual')
    if value.endswith(('.md', '.mdx')):
        surfaces.add('docs')
    if value.endswith(('.json', '.toml', '.yaml', '.yml')):
        surfaces.add('config')
    if value.endswith('.py'):
        surfaces.add('python')
    return surfaces or {'generic'}


def detect_surfaces_for_paths(paths: list[str]) -> set[str]:
    result: set[str] = set()
    for path_value in paths:
        result.update(detect_surface_for_path(path_value))
    return result or {'generic'}
