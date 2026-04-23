from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from .legacy_compat import canonicalize_index_name
from .path_policy import classify_path_policy
from .scanner_contract import REQUIRED_SCANNER_ARTIFACTS

IMPORT_RE = re.compile(r"(?:import\s+(?:[\w*{}, ]+\s+from\s+)?|export\s+[^;]*?from\s+|require\()\s*['\"]([^'\"]+)['\"]")
ROUTE_RE = re.compile(r"path\s*[=:]\s*['\"]([^'\"]+)['\"]")

def classify_kind(relative_path: str) -> str:
    suffix = Path(relative_path).suffix.lower()
    return {
        '.py': 'python',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.json': 'json',
        '.html': 'html',
        '.css': 'css',
        '.md': 'markdown',
    }.get(suffix, 'other')

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return path.read_text(encoding='utf-8', errors='ignore')

def parse_python(path: Path) -> dict[str, Any]:
    source = read_text(path)
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {'ok': False, 'imports': [], 'exports': [], 'error': {'message': exc.msg, 'lineno': exc.lineno}}
    imports: list[str] = []
    exports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append('.' * node.level + (node.module or ''))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and getattr(node, 'col_offset', 1) == 0:
            exports.append(node.name)
    return {'ok': True, 'imports': sorted(set(imports)), 'exports': sorted(set(exports)), 'error': None}

def parse_text_surface(text: str, relative_path: str) -> dict[str, Any]:
    rel = relative_path.lower()
    boundaries: list[str] = []
    if rel.endswith('src/main.tsx'):
        boundaries.append('runtime_entry')
    if rel.endswith('routes/register.ts'):
        boundaries.append('route_registration')
    if 'bridge' in rel or 'qwebchannel' in text.lower():
        boundaries.append('desktop_bridge_boundary')
    if rel.endswith('modules.config.json'):
        boundaries.append('public_registry_boundary')
    if 'i18n' in text.lower():
        boundaries.append('i18n_boundary')
    routes = sorted(set(value.strip() for value in ROUTE_RE.findall(text) if value.strip()))
    imports = sorted(set(value.strip() for value in IMPORT_RE.findall(text) if value.strip()))
    surface_kind = 'module'
    if rel.endswith('main.tsx'):
        surface_kind = 'entrypoint'
    elif '/routes/' in rel or rel.endswith('routes/register.ts'):
        surface_kind = 'route_surface'
    elif '/pages/' in rel:
        surface_kind = 'screen'
    elif '/components/' in rel:
        surface_kind = 'component'
    elif 'bridge' in rel:
        surface_kind = 'desktop_bridge'
    elif rel.endswith('modules.config.json'):
        surface_kind = 'module_config'
    return {'surface_kind': surface_kind, 'routes': routes, 'imports': imports, 'boundaries': boundaries}

def scan_tree(target_root: Path) -> dict[str, Any]:
    modules: list[dict[str, Any]] = []
    boundaries: list[dict[str, Any]] = []
    paths: list[dict[str, Any]] = []
    legacy_seen = False
    for path in sorted(p for p in target_root.rglob('*') if p.is_file()):
        relative_path = path.relative_to(target_root).as_posix()
        policy = classify_path_policy(relative_path)
        path_record = {
            'path': relative_path,
            'action': policy.action,
            'reason': policy.reason,
            'canonical_source': policy.canonical_source,
            'non_product_class': policy.non_product_class,
        }
        paths.append(path_record)
        if policy.action == 'exclude':
            continue
        kind = classify_kind(relative_path)
        record = {
            'path': relative_path,
            'kind': kind,
            'canonical_source': policy.canonical_source,
            'non_product_class': policy.non_product_class,
            'imports': [],
            'exports': [],
            'routes': [],
            'boundaries': [],
        }
        if kind == 'python':
            parsed = parse_python(path)
            record['imports'] = parsed['imports']
            record['exports'] = parsed['exports']
            record['parse_ok'] = parsed['ok']
            record['error'] = parsed['error']
        elif kind in {'typescript', 'javascript', 'json', 'html', 'css', 'markdown'}:
            text = read_text(path)
            parsed = parse_text_surface(text, relative_path)
            record.update(parsed)
            if 'query_index.json' in text:
                _, legacy_seen = canonicalize_index_name('query_index.json')
        modules.append(record)
        for item in record['boundaries']:
            boundaries.append({'source_path': relative_path, 'boundary_kind': item, 'canonical_source': policy.canonical_source})
    summary = {
        'status': 'observed_only',
        'required_artifacts': list(REQUIRED_SCANNER_ARTIFACTS),
        'module_count': len(modules),
        'boundary_count': len(boundaries),
        'path_count': len(paths),
        'excluded_count': sum(1 for item in paths if item['action'] == 'exclude'),
        'observe_only_count': sum(1 for item in paths if item['action'] == 'observe_only'),
        'canonical_count': sum(1 for item in paths if item['action'] == 'canonical'),
        'legacy_query_index_shim_used': legacy_seen,
    }
    return {
        'scan_observed_modules.json': modules,
        'scan_observed_boundaries.json': boundaries,
        'scan_observed_paths.json': paths,
        'scan_observed_summary.json': summary,
    }
