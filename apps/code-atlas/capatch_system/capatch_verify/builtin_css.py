#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Dependency-free CSS sanity verifier for mutating style patches."""

from pathlib import Path
from .base import VerifierResultRow, existing_target_files

CONFLICT_MARKERS = ('<<<<<<<', '=======', '>>>>>>>')


def _comment_issue(text: str) -> str | None:
    i = 0
    while i < len(text):
        start = text.find('/*', i)
        if start == -1:
            break
        end = text.find('*/', start + 2)
        if end == -1:
            return f'unclosed CSS comment starting at offset {start}'
        i = end + 2
    stray = text.find('*/')
    first_open = text.find('/*')
    if stray != -1 and (first_open == -1 or stray < first_open):
        return f'stray CSS comment terminator at offset {stray}'
    return None


def _brace_issue(text: str) -> str | None:
    depth = 0
    in_comment = False
    in_string: str | None = None
    escaped = False
    line = 1
    col = 0
    for idx, char in enumerate(text):
        if char == '\n':
            line += 1
            col = 0
        else:
            col += 1
        nxt = text[idx + 1] if idx + 1 < len(text) else ''
        if in_comment:
            if char == '*' and nxt == '/':
                in_comment = False
            continue
        if in_string:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == in_string:
                in_string = None
            continue
        if char == '/' and nxt == '*':
            in_comment = True
            continue
        if char in {'"', "'"}:
            in_string = char
            continue
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth < 0:
                return f'unmatched closing brace at line {line}, column {col}'
    if in_string:
        return 'unclosed CSS string literal'
    if in_comment:
        return 'unclosed CSS comment'
    if depth != 0:
        return f'unbalanced CSS braces: depth={depth}'
    return None


def _marker_issue(text: str) -> str | None:
    starts: list[int] = []
    ends: list[int] = []
    for no, line in enumerate(text.splitlines(), start=1):
        upper = line.upper()
        if ('CAPATCH' in upper or 'VISUAL-SURGERY' in upper) and 'START' in upper:
            starts.append(no)
        if ('CAPATCH' in upper or 'VISUAL-SURGERY' in upper) and 'END' in upper:
            ends.append(no)
    if len(starts) != len(ends):
        return f'broken CSS markers: START count={len(starts)} END count={len(ends)}'
    for sline, eline in zip(starts, ends):
        if eline < sline:
            return f'broken CSS markers: END appears before START near line {eline}'
    return None


def _line_issue(text: str) -> str | None:
    for no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if any(marker in stripped for marker in CONFLICT_MARKERS):
            return f'git conflict marker found at line {no}'
        low = stripped.lower()
        if '<script' in low or '</div>' in low or '</span>' in low:
            return f'obvious non-CSS/HTML residue at line {no}'
        if stripped.startswith(('export ', 'import ')):
            return f'obvious JS/TS residue at line {no}'
    return None


def _check_css(path: Path) -> tuple[bool, str, dict[str, object]]:
    raw = path.read_bytes()
    if b'\x00' in raw:
        return False, 'NUL byte found in CSS file', {'file': str(path), 'bytes': len(raw)}
    text = raw.decode('utf-8', errors='replace')
    issues: list[str] = []
    for checker in (_comment_issue, _brace_issue, _marker_issue, _line_issue):
        issue = checker(text)
        if issue:
            issues.append(issue)
    metrics = {'file': str(path), 'bytes': len(raw), 'lines': len(text.splitlines()), 'brace_open_count': text.count('{'), 'brace_close_count': text.count('}')}
    if issues:
        return False, '; '.join(issues[:8]), metrics
    return True, 'CSS sanity checks passed', metrics


def run_css_sanity(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in existing_target_files(target_files, ctx):
        if path.suffix.lower() != '.css':
            continue
        try:
            ok, detail, metrics = _check_css(path)
        except Exception as exc:
            ok, detail, metrics = False, f'{type(exc).__name__}: {exc}', {'file': str(path)}
        title = f"CSS sanity {'OK' if ok else 'failed'}: {path.name}"
        rows.append(VerifierResultRow('css-sanity', ok, title, detail, metrics=metrics).to_dict())
    return rows
