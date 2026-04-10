#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Verifier requirement matrix for Phase 0 ownership E."""

from pathlib import Path
from typing import Any

from ._helpers import get_attr_or_key


def compute_required_verifiers(risk_summary: dict[str, Any], target_files: list[str]) -> list[str]:
    required: list[str] = []
    files = [str(item) for item in list(target_files or []) if str(item)]
    for item in files:
        path = Path(item)
        name = path.name.lower()
        suffix = path.suffix.lower()
        if suffix == '.py':
            required.append('python-parse')
            if name == '__init__.py' or 'export' in path.as_posix().lower():
                required.append('export-contract')
            else:
                required.append('python-import-smoke')
        elif suffix == '.json':
            required.append('json-parse')
        elif suffix in {'.yaml', '.yml'}:
            required.append('yaml-parse')
        elif suffix == '.toml':
            required.append('toml-parse')
        elif suffix in {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'}:
            required.append('typescript-parse')
    if bool(get_attr_or_key(risk_summary, 'touches_packaging', False)):
        required.append('build')
    if bool(get_attr_or_key(risk_summary, 'command_based', False)):
        required.extend(['build', 'tests'])
    if files:
        required.append('git-clean')

    ordered: list[str] = []
    seen = set()
    for item in required:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered
