from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED = {
    'files_scanned': 101,
    'source_files': 25,
    'edges': 163,
    'internal_edges': 45,
    'external_edges': 118,
    'unresolved_edges': 0,
}
REQUIRED_FILES = [
    'dependency_map_raw_prisma-control-center_260521_180055.json',
    'code_atlas_dependency_consumer_v03_prisma-control-center_260521_1800_graph.json',
    'code_atlas_dependency_consumer_v03_prisma-control-center_260521_1800_summary.json',
    'code_atlas_dependency_consumer_v03_prisma-control-center_260521_1800_report.md',
    'code_atlas_dependency_consumer_v03_prisma-control-center_260521_1800_tree.txt',
    'code_atlas_dependency_consumer_v03_prisma-control-center_260521_1800_unresolved.md',
    'code_atlas_dependency_visual_v04_2_terminal-de-venta-system_prisma-control-center_Black_Glass_Atlas_260521_180055.html',
    'DEPENDENCY_ATLAS_MANIFEST.json',
    'README_DEPENDENCY_ATLAS_PRISMA_CONTROL_CENTER.md',
]
REQUIRED_INTERNAL_NODE_PATHS = {
    'internal/py/prisma_control_center.py',
    'internal/py/panel_3150.py',
    'internal/py/health_checks.py',
    'internal/py/config_loader.py',
    'internal/py/safe_actions.py',
}


def fail(message: str) -> int:
    print(json.dumps({'ok': False, 'status': 'FAIL', 'error': message}, indent=2, ensure_ascii=False))
    return 1


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    parser = argparse.ArgumentParser(description='Verify PRISMA Control Center dependency atlas bundle install.')
    parser.add_argument('--root', default='.', help='Path to prisma-control-center root.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    atlas = root / 'internal' / 'docs' / 'dependency-atlas'
    if not root.exists():
        return fail(f'root not found: {root}')
    if not atlas.exists():
        return fail(f'dependency atlas dir not found: {atlas}')

    missing = [name for name in REQUIRED_FILES if not (atlas / name).is_file()]
    if missing:
        return fail('missing atlas files: ' + ', '.join(missing))

    cmd = root / '04_ABRIR_ATLAS_DEPENDENCIAS.cmd'
    wrapper = root / 'internal' / 'wrappers' / 'open_dependency_atlas.ps1'
    if not cmd.is_file():
        return fail(f'missing launcher: {cmd}')
    if not wrapper.is_file():
        return fail(f'missing wrapper: {wrapper}')

    summary = read_json(atlas / 'code_atlas_dependency_consumer_v03_prisma-control-center_260521_1800_summary.json')
    graph = read_json(atlas / 'code_atlas_dependency_consumer_v03_prisma-control-center_260521_1800_graph.json')
    raw = read_json(atlas / 'dependency_map_raw_prisma-control-center_260521_180055.json')
    manifest = read_json(atlas / 'DEPENDENCY_ATLAS_MANIFEST.json')

    dep = summary.get('dependency_summary', {})
    mismatches = []
    for key, expected in EXPECTED.items():
        got = dep.get(key)
        if got != expected:
            mismatches.append({'field': key, 'expected': expected, 'actual': got})
    if mismatches:
        return fail('dependency summary mismatch: ' + json.dumps(mismatches, ensure_ascii=False))

    languages = set(summary.get('project_profile', {}).get('languages', []))
    if not {'JavaScript (8)', 'Python (17)'}.issubset(languages):
        return fail('language counts do not match expected JavaScript (8), Python (17)')

    raw_root = str(raw.get('root', '')).replace('/', '\\').lower()
    if not raw_root.endswith('terminal-de-venta-system\\prisma-control-center'):
        return fail(f'raw atlas root does not point to prisma-control-center: {raw.get("root")}')

    node_paths = {str(node.get('path', '')).replace('\\', '/') for node in graph.get('nodes', [])}
    missing_nodes = sorted(REQUIRED_INTERNAL_NODE_PATHS - node_paths)
    if missing_nodes:
        return fail('missing required graph nodes: ' + ', '.join(missing_nodes))

    unresolved_edges = [edge for edge in graph.get('edges', []) if edge.get('classification') == 'unresolved']
    if unresolved_edges:
        return fail(f'graph contains unresolved edges: {len(unresolved_edges)}')

    html_text = (atlas / 'code_atlas_dependency_visual_v04_2_terminal-de-venta-system_prisma-control-center_Black_Glass_Atlas_260521_180055.html').read_text(encoding='utf-8', errors='replace')
    html_needles = ['Black Glass Atlas', 'Runtime focus', 'Risk signals', 'terminal-de-venta-system / prisma-control-center']
    missing_needles = [needle for needle in html_needles if needle not in html_text]
    if missing_needles:
        return fail('atlas html missing expected markers: ' + ', '.join(missing_needles))

    result = {
        'ok': True,
        'status': 'PASS',
        'bundleId': manifest.get('bundleId'),
        'root': str(root),
        'atlasRoot': str(atlas),
        'summary': EXPECTED,
        'requiredNodeCount': len(REQUIRED_INTERNAL_NODE_PATHS),
        'htmlBytes': len(html_text.encode('utf-8')),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
