from __future__ import annotations

import ast
import re
from pathlib import Path, PurePosixPath
from typing import Any

TEXT_KINDS = {
    '.py': 'python',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.json': 'json',
    '.html': 'html',
    '.css': 'css',
    '.md': 'markdown',
}

IMPORT_RE = re.compile(r"(?:import\s+(?:[\w*{}, ]+\s+from\s+)?|export\s+[^;]*?from\s+|require\()\s*['\"]([^'\"]+)['\"]")
ROUTE_RE = re.compile(r"path\s*[=:]\s*['\"]([^'\"]+)['\"]")


def classify_file(relative_path: str) -> str:
    return TEXT_KINDS.get(Path(relative_path).suffix.lower(), 'other')


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return path.read_text(encoding='utf-8', errors='ignore')


def surface_module_name(relative_path: str) -> str:
    pure = PurePosixPath(relative_path)
    base = pure.as_posix()
    for suffix in pure.suffixes:
        if base.endswith(suffix):
            base = base[:-len(suffix)]
    return base.replace('/', '.').replace('-', '_').strip('.') or 'root'


def detect_surface_kind(relative_path: str, text: str) -> str:
    rel = relative_path.lower()
    name = Path(relative_path).name.lower()
    if rel.endswith('modules.config.json'):
        return 'module_config'
    if '/routes/' in rel or 'router' in name or rel.endswith('routes/register.ts'):
        return 'route_surface'
    if '/pages/' in rel:
        return 'screen'
    if '/components/' in rel:
        return 'component'
    if name == 'main.tsx':
        return 'entrypoint'
    if 'bridge' in name or 'qwebchannel' in text.lower():
        return 'desktop_bridge'
    if rel.endswith('.css'):
        return 'style_asset'
    if rel.endswith('.html'):
        return 'html_asset'
    if rel.endswith('.json'):
        return 'json_asset'
    if rel.endswith(('.ts', '.tsx', '.js', '.jsx')):
        return 'module'
    if rel.endswith('.md'):
        return 'markdown_asset'
    return 'other_asset'


def detect_boundary_kinds(text: str, relative_path: str) -> list[str]:
    rel = relative_path.lower()
    low = text.lower()
    kinds: list[str] = []
    if rel.endswith('src/main.tsx'):
        kinds.append('runtime_entry')
    if rel.endswith('routes/register.ts'):
        kinds.append('route_registration')
    if 'bridge' in rel or 'qwebchannel' in low:
        kinds.append('desktop_bridge_boundary')
    if rel.endswith('modules.config.json'):
        kinds.append('public_registry_boundary')
    if 'i18n' in low:
        kinds.append('i18n_boundary')
    return kinds


def extract_routes(text: str) -> list[str]:
    return sorted(set(v.strip() for v in ROUTE_RE.findall(text) if v.strip()))


def extract_imports(text: str) -> list[str]:
    return sorted(set(v.strip() for v in IMPORT_RE.findall(text) if v.strip()))


def parse_python_file(path: Path) -> dict[str, Any]:
    source = read_text_file(path)
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {
            'ok': False,
            'imports': [],
            'exports': [],
            'error': {'message': exc.msg, 'lineno': exc.lineno, 'offset': exc.offset},
        }
    imports: list[str] = []
    exports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append('.' * node.level + (node.module or ''))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and getattr(node, 'col_offset', 1) == 0:
            exports.append(node.name)
        elif isinstance(node, ast.Assign) and getattr(node, 'col_offset', 1) == 0:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '__all__':
                    try:
                        value = ast.literal_eval(node.value)
                    except Exception:
                        continue
                    if isinstance(value, (list, tuple)):
                        exports.extend(str(item) for item in value)
    return {'ok': True, 'imports': sorted(set(imports)), 'exports': sorted(set(exports)), 'error': None}


def parse_text_surface(path: Path, relative_path: str) -> dict[str, Any]:
    text = read_text_file(path)
    return {
        'ok': True,
        'surface_kind': detect_surface_kind(relative_path, text),
        'imports': extract_imports(text),
        'routes': extract_routes(text),
        'boundaries': detect_boundary_kinds(text, relative_path),
        'module_name': surface_module_name(relative_path),
    }
