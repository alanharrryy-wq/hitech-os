#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from .base import VerifierResultRow, existing_target_files

JS_SUFFIXES = {'.js', '.jsx', '.mjs', '.cjs'}
TS_SUFFIXES = {'.ts', '.tsx'}
HOOK_NAMES = ('useState', 'useEffect', 'useMemo', 'useCallback', 'useReducer', 'useContext', 'useRef')


def _run_command(command: list[str], *, cwd: Path | None = None) -> tuple[bool, str]:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=45, check=False, cwd=str(cwd) if cwd else None)
    except Exception as exc:
        return False, f'{type(exc).__name__}: {exc}'
    output = (completed.stdout or '').strip() or (completed.stderr or '').strip()
    return completed.returncode == 0, output[:2000]


def _brace_balance_ok(text: str) -> bool:
    pairs = {'(': ')', '[': ']', '{': '}'}
    stack: list[str] = []
    for char in text:
        if char in pairs:
            stack.append(pairs[char])
        elif char in pairs.values():
            if not stack or stack.pop() != char:
                return False
    return not stack


def _duplicate_import_lines(text: str) -> list[str]:
    seen: dict[str, int] = {}
    duplicates: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith('import '):
            continue
        seen[stripped] = seen.get(stripped, 0) + 1
        if seen[stripped] == 2:
            duplicates.append(stripped)
    return duplicates


def _hook_boundary_issue(path: Path, text: str) -> str | None:
    suffix = path.suffix.lower()
    if suffix not in TS_SUFFIXES | JS_SUFFIXES:
        return None
    uses_hook = any(re.search(rf'\b{name}\s*\(', text) for name in HOOK_NAMES)
    if not uses_hook:
        return None
    first_lines = '\n'.join(text.splitlines()[:5])
    if "'use client'" in first_lines or '"use client"' in first_lines:
        return None
    return 'react hooks detected without a top-level use client directive'


def _fallback_typescript_checks(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding='utf-8', errors='replace')
    issues: list[str] = []
    if not _brace_balance_ok(text):
        issues.append('unbalanced braces/brackets/parentheses')
    duplicates = _duplicate_import_lines(text)
    if duplicates:
        issues.append('duplicate import lines detected')
    boundary = _hook_boundary_issue(path, text)
    if boundary:
        issues.append(boundary)
    if issues:
        return False, '; '.join(issues[:5])
    return True, 'fallback structural checks passed'


def run_typescript_parse(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    node_bin = shutil.which('node')
    npx_bin = shutil.which('npx')
    root_dir = Path(str(ctx.get('root_dir') or '.')).resolve() if isinstance(ctx, dict) else None
    for path in existing_target_files(target_files, ctx):
        suffix = path.suffix.lower()
        if suffix not in JS_SUFFIXES | TS_SUFFIXES:
            continue
        if suffix in JS_SUFFIXES and node_bin:
            ok, detail = _run_command([node_bin, '--check', str(path)], cwd=root_dir)
        elif suffix in TS_SUFFIXES and npx_bin:
            ok, detail = _run_command([npx_bin, '--yes', 'tsc', '--noEmit', '--pretty', 'false', str(path)], cwd=root_dir)
        else:
            ok, detail = _fallback_typescript_checks(path)
        title = f"TS/JS verification {'OK' if ok else 'failed'}: {path.name}"
        rows.append(VerifierResultRow('typescript-parse', ok, title, detail or str(path), metrics={'file': str(path)}).to_dict())
    return rows
