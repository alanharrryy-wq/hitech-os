#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from .base import VerifierResultRow, existing_target_files

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


def run_yaml_parse(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for path in existing_target_files(target_files, ctx):
        if path.suffix.lower() not in {'.yaml', '.yml'}:
            continue
        if yaml is None:
            rows.append(VerifierResultRow('yaml-parse', False, f'YAML parser unavailable: {path.name}', 'PyYAML no está disponible en este runtime.', metrics={'file': str(path)}).to_dict())
            continue
        try:
            yaml.safe_load(path.read_text(encoding='utf-8', errors='replace'))
            rows.append(VerifierResultRow('yaml-parse', True, f'YAML parse OK: {path.name}', str(path), metrics={'file': str(path)}).to_dict())
        except Exception as exc:
            rows.append(VerifierResultRow('yaml-parse', False, f'YAML parse failed: {path.name}', f'{type(exc).__name__}: {exc}', metrics={'file': str(path)}).to_dict())
    return rows
