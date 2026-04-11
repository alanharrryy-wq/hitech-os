#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json

from .base import VerifierResultRow, existing_target_files


def run_json_parse(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for path in existing_target_files(target_files, ctx):
        if path.suffix.lower() != '.json':
            continue
        try:
            json.loads(path.read_text(encoding='utf-8', errors='replace'))
            rows.append(VerifierResultRow('json-parse', True, f'JSON parse OK: {path.name}', str(path), metrics={'file': str(path)}).to_dict())
        except Exception as exc:
            rows.append(VerifierResultRow('json-parse', False, f'JSON parse failed: {path.name}', f'{type(exc).__name__}: {exc}', metrics={'file': str(path)}).to_dict())
    return rows
