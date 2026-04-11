#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import tomllib

from .base import VerifierResultRow, existing_target_files


def run_toml_parse(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for path in existing_target_files(target_files, ctx):
        if path.suffix.lower() != '.toml':
            continue
        try:
            with path.open('rb') as handle:
                tomllib.load(handle)
            rows.append(VerifierResultRow('toml-parse', True, f'TOML parse OK: {path.name}', str(path), metrics={'file': str(path)}).to_dict())
        except Exception as exc:
            rows.append(VerifierResultRow('toml-parse', False, f'TOML parse failed: {path.name}', f'{type(exc).__name__}: {exc}', metrics={'file': str(path)}).to_dict())
    return rows
