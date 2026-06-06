from __future__ import annotations

import re
from pathlib import Path

from .base import fail

TS_SUFFIXES = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'}


def is_typescript_surface(target: Path) -> bool:
    return target.suffix.lower() in TS_SUFFIXES


def _require_typescript_target(target: Path, label: str) -> None:
    if not is_typescript_surface(target):
        fail(f'{label}: structural typescript operation requires a TS/JS target')


def render_ts_ensure_import(target: Path, text: str, module: str, symbol: str, label: str) -> str:
    _require_typescript_target(target, label)
    pattern = '^import\\s*{[^}]*\\b' + re.escape(symbol) + '\\b[^}]*}\\s*from\\s*[\'\"]' + re.escape(module) + '[\'\"];?\\s*$'
    import_pattern = re.compile(pattern, re.MULTILINE)
    if import_pattern.search(text):
        return text
    lines = text.splitlines()
    insert_at = 0
    for index, line in enumerate(lines):
        if line.strip().startswith('import '):
            insert_at = index + 1
    lines.insert(insert_at, f"import {{ {symbol} }} from '{module}';")
    return '\n'.join(lines) + ('\n' if text.endswith('\n') else '')


def render_ts_insert_object_key(target: Path, text: str, anchor: str, new_entry: str, label: str) -> str:
    _require_typescript_target(target, label)
    token = str(anchor or '').strip()
    if not token:
        fail(f'{label}: object anchor is required')
    if token not in text:
        fail(f'{label}: object anchor not found')
    if new_entry.strip() in text:
        return text
    replacement = token + '\n' + new_entry.rstrip()
    return text.replace(token, replacement, 1)


def render_ts_wrap_jsx_text(target: Path, text: str, literal_text: str, replacement_expr: str, label: str) -> str:
    _require_typescript_target(target, label)
    needle = str(literal_text or '')
    if not needle or needle not in text:
        fail(f'{label}: jsx literal not found')
    replacement = '{' + str(replacement_expr).strip() + '}'
    return text.replace(needle, replacement, 1)
