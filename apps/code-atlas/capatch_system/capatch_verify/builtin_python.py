#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import ast
import py_compile
from typing import Any

from .base import VerifierResultRow, existing_target_files


def run_python_parse(target_files: list[str], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for path in existing_target_files(target_files, ctx):
        if path.suffix.lower() != '.py':
            continue
        try:
            ast.parse(path.read_text(encoding='utf-8', errors='replace'), filename=str(path))
            rows.append(VerifierResultRow('python-parse', True, f'Python parse OK: {path.name}', str(path), metrics={'file': str(path)}).to_dict())
        except Exception as exc:
            rows.append(VerifierResultRow('python-parse', False, f'Python parse failed: {path.name}', f'{type(exc).__name__}: {exc}', metrics={'file': str(path)}).to_dict())
    return rows


def run_python_import_smoke(target_files: list[str], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for path in existing_target_files(target_files, ctx):
        if path.suffix.lower() != '.py':
            continue
        try:
            py_compile.compile(str(path), doraise=True)
            rows.append(VerifierResultRow('python-import-smoke', True, f'Python compile OK: {path.name}', str(path), metrics={'file': str(path)}).to_dict())
        except Exception as exc:
            rows.append(VerifierResultRow('python-import-smoke', False, f'Python compile failed: {path.name}', f'{type(exc).__name__}: {exc}', metrics={'file': str(path)}).to_dict())
    return rows


def run_export_contract(target_files: list[str], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for path in existing_target_files(target_files, ctx):
        if path.name != '__init__.py':
            continue
        try:
            source = path.read_text(encoding='utf-8', errors='replace')
            ast.parse(source, filename=str(path))
            rows.append(VerifierResultRow('export-contract', True, f'Export contract parse OK: {path.name}', str(path), metrics={'file': str(path)}).to_dict())
        except Exception as exc:
            rows.append(VerifierResultRow('export-contract', False, f'Export contract failed: {path.name}', f'{type(exc).__name__}: {exc}', metrics={'file': str(path)}).to_dict())
    return rows
