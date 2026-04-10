#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import shutil
import subprocess

from .base import VerifierResultRow, existing_target_files


JS_SUFFIXES = {'.js', '.jsx', '.mjs', '.cjs'}
TS_SUFFIXES = {'.ts', '.tsx'}


def _run_command(command: list[str]) -> tuple[bool, str]:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=45, check=False)
    except Exception as exc:
        return False, f'{type(exc).__name__}: {exc}'
    output = (completed.stdout or '').strip() or (completed.stderr or '').strip()
    return completed.returncode == 0, output[:2000]


def run_typescript_parse(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    node_bin = shutil.which('node')
    npx_bin = shutil.which('npx')
    for path in existing_target_files(target_files, ctx):
        suffix = path.suffix.lower()
        if suffix not in JS_SUFFIXES | TS_SUFFIXES:
            continue
        if suffix in JS_SUFFIXES and node_bin:
            ok, detail = _run_command([node_bin, '--check', str(path)])
        elif suffix in TS_SUFFIXES and npx_bin:
            ok, detail = _run_command([npx_bin, '--yes', 'tsc', '--noEmit', '--pretty', 'false', str(path)])
        else:
            ok = False
            detail = 'No hay runtime de Node/npx disponible para verificar este archivo.'
        rows.append(VerifierResultRow('typescript-parse', ok, f'TS/JS verification {"OK" if ok else "failed"}: {path.name}', detail or str(path), metrics={'file': str(path)}).to_dict())
    return rows
