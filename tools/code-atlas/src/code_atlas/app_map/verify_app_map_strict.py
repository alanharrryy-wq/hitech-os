# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import zipfile
from pathlib import Path

try:
    from .runner import run_app_map
    from .strict_classifier import is_valid_selector, is_route_file
except Exception:
    from runner import run_app_map  # type: ignore
    from strict_classifier import is_valid_selector, is_route_file  # type: ignore

BAD_ROUTE_SUFFIXES = {'.css','.scss','.json','.jsonc','.md','.txt','.yaml','.yml'}
RAW_BAD_SUFFIXES = {'.db','.sqlite','.sqlite3'}


def validate_zip(zip_path: Path) -> dict:
    errors=[]; warnings=[]
    with tempfile.TemporaryDirectory(prefix='appmap_strict_') as td:
        td=Path(td)
        with zipfile.ZipFile(zip_path,'r') as z:
            z.extractall(td)
        root = td/'app_map_atlas'
        route_map = json.loads((root/'02_ROUTE_COMPONENT_MAP.json').read_text(encoding='utf-8'))
        selectors = json.loads((root/'05_SELECTOR_GRAPH.json').read_text(encoding='utf-8'))
        tokens = json.loads((root/'07_TOKEN_GRAPH.json').read_text(encoding='utf-8'))
        surfaces = json.loads((root/'01_SURFACE_REGISTRY.json').read_text(encoding='utf-8'))
        file_index = json.loads((root/'18_FILE_CLASSIFICATION_INDEX.json').read_text(encoding='utf-8'))
        for row in route_map:
            f = str(row.get('file',''))
            if any(f.endswith(s) for s in BAD_ROUTE_SUFFIXES):
                errors.append(f'ROUTE_MAP_NON_ROUTE_FILE:{f}')
            if row.get('fileKind') != 'route':
                errors.append(f'ROUTE_MAP_BAD_FILE_KIND:{f}:{row.get("fileKind")}')
            if not str(row.get('route','')).startswith('/'):
                errors.append(f'ROUTE_MAP_BAD_ROUTE:{row}')
        for row in selectors:
            s = str(row.get('selector',''))
            if not is_valid_selector(s):
                errors.append(f'SELECTOR_GRAPH_INVALID:{s[:120]}')
            if '--' in s or ';' in s or re.search(r'\n\s*(?:--[\w-]+|[a-zA-Z-]+)\s*:', s):
                errors.append(f'SELECTOR_GRAPH_DECLARATION_LEAK:{s[:120]}')
            if row.get('fileKind') != 'style':
                errors.append(f'SELECTOR_GRAPH_BAD_FILE_KIND:{row.get("definedIn")}: {row.get("fileKind")}')
        for row in tokens:
            if not str(row.get('token','')).startswith('--'):
                errors.append(f'TOKEN_GRAPH_BAD_TOKEN:{row}')
            if row.get('fileKind') != 'style':
                errors.append(f'TOKEN_GRAPH_BAD_FILE_KIND:{row.get("definedOrUsedIn")}: {row.get("fileKind")}')
        for row in surfaces:
            sid = str(row.get('surfaceId',''))
            if '/' in sid or sid.endswith(('.css','.json','.tsx','.ts','.md')):
                errors.append(f'SURFACE_REGISTRY_FILE_LEAK:{sid}')
        for p in root.rglob('*'):
            if p.is_file() and p.suffix.lower() in RAW_BAD_SUFFIXES:
                errors.append(f'RAW_DB_INCLUDED:{p.name}')
            if p.name.startswith('.env'):
                errors.append(f'ENV_INCLUDED:{p.name}')
    return {'ok': not errors, 'errors': errors[:200], 'warnings': warnings, 'zip': str(zip_path)}


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo-root', default=os.getcwd())
    ap.add_argument('--target-app', default='tablet')
    ap.add_argument('--output-root', default=None)
    ap.add_argument('--json-out', default=None)
    ns=ap.parse_args(argv)
    out = Path(ns.output_root or tempfile.mkdtemp(prefix='appmap_verify_out_'))
    out.mkdir(parents=True, exist_ok=True)
    z = Path(run_app_map(ns.repo_root, target_app=ns.target_app, output_root=str(out)))
    result = validate_zip(z)
    result['status'] = 'PASS_APP_MAP_STRICT_CLASSIFICATION_VERIFIED' if result['ok'] else 'FAIL_APP_MAP_STRICT_CLASSIFICATION'
    if ns.json_out:
        Path(ns.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(ns.json_out).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
