#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Risk classifier aligned to hardened Phase 1 policy."""

from typing import Any, Iterable

from ._helpers import get_attr_or_key, normalize_target_files, path_name_suffix
from .verification_requirements import compute_verification_policy

READ_ONLY_OPERATION_TYPES = {
    'AssertContains',
    'AssertNotContains',
    'AssertRegexCount',
    'AssertFileExists',
    'AssertFileNotExists',
}

SENSITIVE_FILENAMES = {
    '__init__.py',
    'pyproject.toml',
    'package.json',
    'package-lock.json',
    'pnpm-lock.yaml',
    'yarn.lock',
    'tsconfig.json',
    'vite.config.ts',
    'vite.config.js',
}

UI_HINTS = {'gui', 'ui', 'window', 'focus', 'input', 'renderer', 'view', 'screen', 'overlay', 'widget'}
PYTHON_RUNTIME_HINTS = {'runtime', 'plugin', 'policy', 'verifier', 'engine', 'executor', 'pipeline', 'bootstrap', 'entrypoint'}
STRUCTURAL_SUFFIXES = {'.ts', '.tsx', '.js', '.jsx'}


def _operation_type(operation: Any) -> str:
    spec = get_attr_or_key(operation, 'spec')
    return str(get_attr_or_key(operation, 'type', get_attr_or_key(spec, 'type', '')) or '')


def classify_change(preflight: Any, operations: Iterable[Any]) -> dict[str, Any]:
    operations = list(operations or [])
    target_files = normalize_target_files(preflight, operations)
    mutating = [item for item in operations if _operation_type(item) not in READ_ONLY_OPERATION_TYPES]
    read_only = [item for item in operations if _operation_type(item) in READ_ONLY_OPERATION_TYPES]
    conflicts = list(get_attr_or_key(preflight, 'conflicts', []) or [])
    path_violations = list(get_attr_or_key(preflight, 'path_violations', []) or [])
    schema_violations = list(get_attr_or_key(preflight, 'schema_violations', []) or [])
    surface_summary = dict(get_attr_or_key(preflight, 'surface_summary', {}) or {})
    anchor_diagnostics = dict(get_attr_or_key(preflight, 'anchor_diagnostics', {}) or {})
    strategy_hints = dict(get_attr_or_key(preflight, 'strategy_hints', {}) or {})
    blockers: list[str] = []
    reasons: list[str] = []
    recommended_guardrails: list[str] = []

    if conflicts:
        blockers.append(f'conflicts={len(conflicts)}')
    if path_violations:
        blockers.append(f'path_violations={len(path_violations)}')
    if schema_violations:
        blockers.append(f'schema_violations={len(schema_violations)}')

    touches_sensitive = False
    touches_ui = False
    touches_packaging = False
    touches_python_runtime = False
    touches_entrypoints = False
    structural_candidate_files = sorted({str(item) for item in list(surface_summary.get('structural_candidate_files') or strategy_hints.get('structural_candidate_files') or []) if str(item)})
    has_structural_surface = False
    for item in target_files:
        name, suffix = path_name_suffix(item)
        lowered = item.lower()
        if name in SENSITIVE_FILENAMES:
            touches_sensitive = True
        if name in {'pyproject.toml', 'setup.cfg', 'setup.py', 'package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock'}:
            touches_packaging = True
        if any(token in lowered for token in UI_HINTS) or suffix in {'.tsx', '.jsx'}:
            touches_ui = True
        if suffix in STRUCTURAL_SUFFIXES:
            has_structural_surface = True
        if suffix == '.py' and (name in {'__main__.py', 'main.py', 'cli.py', 'app.py'} or any(token in lowered for token in PYTHON_RUNTIME_HINTS)):
            touches_python_runtime = True
            if name in {'__main__.py', 'main.py', 'cli.py', 'app.py'} or 'entrypoint' in lowered or 'bootstrap' in lowered:
                touches_entrypoints = True

    operation_count = len(operations)
    fragile_anchor_count = int(anchor_diagnostics.get('fragile_anchor_operation_count', 0) or 0)
    exact_anchor_count = int(anchor_diagnostics.get('exact_anchor_operation_count', 0) or 0)
    high_density_files = list(anchor_diagnostics.get('high_density_files') or [])
    mutating_count = len(mutating)
    risk_level = 'low'
    risk_tier = 'safe'

    if blockers:
        risk_level = 'critical'
        risk_tier = 'blocked'
        recommended_guardrails.extend(['probe-only', 'manual-review'])
    elif operation_count == 0:
        risk_level = 'medium'
        risk_tier = 'guarded'
        reasons.append('no operations provided')
        recommended_guardrails.append('probe-only')
    elif len(target_files) == 1 and mutating_count <= 3 and not touches_sensitive and not touches_ui and not touches_packaging and not touches_python_runtime and fragile_anchor_count == 0:
        risk_level = 'low'
        risk_tier = 'safe'
    elif len(target_files) <= 3 and mutating_count <= 8 and not touches_sensitive and not touches_ui and not touches_packaging and fragile_anchor_count <= 1:
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
    if touches_python_runtime:
        reasons.append('touches python runtime or orchestration surface')
    if touches_entrypoints:
        reasons.append('touches python entrypoints')
    if len(target_files) > 3:
        reasons.append(f'multi-file change count={len(target_files)}')
    if mutating_count > 8:
        reasons.append(f'mutating_operation_count={mutating_count}')
    if fragile_anchor_count:
        reasons.append(f'fragile_anchor_count={fragile_anchor_count}')
    if high_density_files:
        reasons.append(f'high_density_files={len(high_density_files)}')
    if structural_candidate_files:
        reasons.append(f'structural_candidate_files={len(structural_candidate_files)}')
    if int(surface_summary.get('regex_operation_count', 0) or 0) > 0:
        reasons.append(f"regex_operation_count={int(surface_summary.get('regex_operation_count', 0) or 0)}")
    if int(surface_summary.get('semantic_operation_count', 0) or 0) > 0:
        reasons.append(f"semantic_operation_count={int(surface_summary.get('semantic_operation_count', 0) or 0)}")

    if risk_level in {'high', 'critical'}:
        recommended_guardrails.append('dry-run-required')
    if has_structural_surface or structural_candidate_files:
        recommended_guardrails.append('strategy-review')
    if fragile_anchor_count:
        recommended_guardrails.append('anchor-review')
    if len(target_files) > 1:
        recommended_guardrails.append('transaction-review')
    if not recommended_guardrails:
        recommended_guardrails.append('standard-verification')

    summary = {
        'risk_level': risk_level,
        'risk_tier': risk_tier,
        'target_files': target_files,
        'operation_count': operation_count,
        'mutating_operation_count': mutating_count,
        'read_only_operation_count': len(read_only),
        'touches_sensitive': touches_sensitive,
        'touches_packaging': touches_packaging,
        'touches_ui': touches_ui,
        'touches_python_runtime': touches_python_runtime,
        'touches_entrypoints': touches_entrypoints,
        'command_based': False,
        'blocked_reasons': blockers,
        'reasons': reasons,
        'surface_summary': surface_summary,
        'anchor_diagnostics': anchor_diagnostics,
        'strategy_hints': strategy_hints,
        'structural_candidate_files': structural_candidate_files,
        'has_structural_surface': has_structural_surface or bool(structural_candidate_files),
        'fragile_anchor_count': fragile_anchor_count,
        'exact_anchor_count': exact_anchor_count,
        'high_density_files': high_density_files,
        'recommended_guardrails': sorted(dict.fromkeys(recommended_guardrails)),
    }
    policy = compute_verification_policy(summary, target_files)
    summary['required_verifiers'] = list(policy.get('required_verifiers') or [])
    summary['verification_floor'] = str(policy.get('verification_floor') or 'none')
    summary['verification_packs'] = list(policy.get('packs') or [])
    summary['allow_applied_no_verifiers'] = bool(policy.get('allow_applied_no_verifiers', False))
    summary['surface_flags'] = dict(policy.get('surface_flags') or {})
    return summary
