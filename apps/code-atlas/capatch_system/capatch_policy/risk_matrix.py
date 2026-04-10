#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Risk classifier aligned to the Phase 0 master spec."""

from pathlib import Path
from typing import Any, Iterable

from ._helpers import get_attr_or_key, normalize_target_files, path_suffixes
from .verification_requirements import compute_required_verifiers

READ_ONLY_OPERATION_TYPES = {
    "AssertContains",
    "AssertNotContains",
    "AssertRegexCount",
    "AssertFileExists",
    "AssertFileNotExists",
}

SENSITIVE_FILENAMES = {
    "__init__.py",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "tsconfig.json",
    "vite.config.ts",
    "vite.config.js",
}

UI_HINTS = {"gui", "ui", "window", "focus", "input", "renderer", "view", "screen"}


def _operation_type(operation: Any) -> str:
    spec = get_attr_or_key(operation, 'spec')
    return str(get_attr_or_key(operation, 'type', get_attr_or_key(spec, 'type', '')) or '')


def _operation_file(operation: Any) -> str:
    spec = get_attr_or_key(operation, 'spec')
    return str(get_attr_or_key(operation, 'file', get_attr_or_key(spec, 'file', '')) or '')


def classify_change(preflight: Any, operations: Iterable[Any]) -> dict[str, Any]:
    operations = list(operations or [])
    target_files = normalize_target_files(preflight, operations)
    mutating = [item for item in operations if _operation_type(item) not in READ_ONLY_OPERATION_TYPES]
    read_only = [item for item in operations if _operation_type(item) in READ_ONLY_OPERATION_TYPES]
    conflicts = list(get_attr_or_key(preflight, 'conflicts', []) or [])
    path_violations = list(get_attr_or_key(preflight, 'path_violations', []) or [])
    schema_violations = list(get_attr_or_key(preflight, 'schema_violations', []) or [])
    blockers: list[str] = []
    reasons: list[str] = []

    if conflicts:
        blockers.append(f"conflicts={len(conflicts)}")
    if path_violations:
        blockers.append(f"path_violations={len(path_violations)}")
    if schema_violations:
        blockers.append(f"schema_violations={len(schema_violations)}")

    touches_sensitive = False
    touches_ui = False
    touches_packaging = False
    for item in target_files:
        name, suffix = path_suffixes(item)
        lowered = item.lower()
        if name in SENSITIVE_FILENAMES or suffix in {'.toml'}:
            touches_sensitive = True
        if name in {'pyproject.toml', 'package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock'}:
            touches_packaging = True
        if any(token in lowered for token in UI_HINTS):
            touches_ui = True
        if suffix in {'.tsx', '.jsx'}:
            touches_ui = True

    operation_count = len(operations)
    risk_level = 'low'
    risk_tier = 'safe'

    if blockers:
        risk_level = 'critical'
        risk_tier = 'blocked'
    elif operation_count == 0:
        risk_level = 'medium'
        risk_tier = 'guarded'
        reasons.append('no operations provided')
    elif len(target_files) == 1 and len(mutating) <= 3 and not touches_sensitive and not touches_ui and not touches_packaging:
        risk_level = 'low'
        risk_tier = 'safe'
    elif len(target_files) <= 3 and not touches_sensitive and not touches_ui:
        risk_level = 'medium'
        risk_tier = 'guarded'
    else:
        risk_level = 'high'
        risk_tier = 'high-risk'

    if touches_packaging:
        reasons.append('touches packaging or manifests')
    if touches_sensitive:
        reasons.append('touches exports/bootstrap/sensitive files')
    if touches_ui:
        reasons.append('touches ui or focus/input surfaces')
    if len(target_files) > 3:
        reasons.append(f'multi-file change count={len(target_files)}')
    if len(mutating) > 8:
        reasons.append(f'mutating_operation_count={len(mutating)}')

    risk_summary = {
        'risk_level': risk_level,
        'risk_tier': risk_tier,
        'target_files': target_files,
        'operation_count': operation_count,
        'mutating_operation_count': len(mutating),
        'read_only_operation_count': len(read_only),
        'touches_sensitive': touches_sensitive,
        'touches_packaging': touches_packaging,
        'touches_ui': touches_ui,
        'blocked_reasons': blockers,
        'reasons': reasons,
    }
    risk_summary['required_verifiers'] = compute_required_verifiers(risk_summary, target_files)
    return risk_summary
