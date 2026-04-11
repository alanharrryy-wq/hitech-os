#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Verification requirement matrix aligned to hardened Phase 1 policy.

Phase 1 goals:
- kill the fake green from python-import-smoke
- forbid success without the minimum evidence floor
- derive required verifiers from change surface, not only extension
"""

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

VERIFICATION_FLOORS = ('none', 'syntax', 'runtime', 'domain', 'operational')
_FLOOR_RANK = {name: index for index, name in enumerate(VERIFICATION_FLOORS)}

_SAFE_TEXT_SUFFIXES = {
    '.md', '.txt', '.rst', '.csv', '.log', '.ini', '.cfg', '.conf', '.ps1', '.bat', '.cmd', '.sh', '.zsh', '.bash', '.dockerignore', '.gitignore'
}
_PACKAGING_NAMES = {
    'pyproject.toml',
    'setup.cfg',
    'setup.py',
    'package.json',
    'package-lock.json',
    'pnpm-lock.yaml',
    'yarn.lock',
}
_PYTHON_ENTRYPOINT_NAMES = {'__main__.py', 'main.py', 'cli.py', 'app.py', 'bootstrap.py', 'entrypoint.py'}
_PYTHON_ENTRYPOINT_HINTS = ('bootstrap', 'entrypoint', 'runtime', 'launch', 'startup')
_PUBLIC_API_HINTS = ('export', 'public_api', 'contract', 'api')
_GUI_HINTS = ('gui', 'ui', 'window', 'focus', 'input', 'renderer', 'view', 'screen', 'overlay', 'widget')
_RUNTIME_HINTS = ('runtime', 'plugin', 'policy', 'verifier', 'engine', 'executor', 'pipeline')


@dataclass(slots=True)
class VerificationPolicy:
    required_verifiers: list[str] = field(default_factory=list)
    verification_floor: str = 'none'
    packs: list[str] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)
    surface_flags: dict[str, bool] = field(default_factory=dict)
    allow_applied_no_verifiers: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            'required_verifiers': list(self.required_verifiers),
            'verification_floor': str(self.verification_floor),
            'packs': list(self.packs),
            'reason_codes': list(self.reason_codes),
            'surface_flags': dict(self.surface_flags),
            'allow_applied_no_verifiers': bool(self.allow_applied_no_verifiers),
        }


def _raise_floor(current: str, wanted: str) -> str:
    current_key = current if current in _FLOOR_RANK else 'none'
    wanted_key = wanted if wanted in _FLOOR_RANK else 'none'
    return wanted_key if _FLOOR_RANK[wanted_key] > _FLOOR_RANK[current_key] else current_key


def _dedupe(items: list[str]) -> list[str]:
    ordered: list[str] = []
    seen = set()
    for item in list(items or []):
        token = str(item or '').strip()
        if not token or token in seen:
            continue
        seen.add(token)
        ordered.append(token)
    return ordered


def _touches_packaging(files: list[str], risk_summary: dict[str, Any]) -> bool:
    if bool((risk_summary or {}).get('touches_packaging', False)):
        return True
    return any(Path(item).name.lower() in _PACKAGING_NAMES for item in list(files or []))


def _touches_public_api(path: Path) -> bool:
    lowered = path.as_posix().lower()
    if path.name == '__init__.py':
        return True
    return any(token in lowered for token in _PUBLIC_API_HINTS)


def _touches_entrypoint(path: Path) -> bool:
    lowered = path.as_posix().lower()
    if path.name.lower() in _PYTHON_ENTRYPOINT_NAMES:
        return True
    return any(token in lowered for token in _PYTHON_ENTRYPOINT_HINTS)


def _surface_flags(files: list[str], risk_summary: dict[str, Any]) -> dict[str, bool]:
    flags = {
        'touches_python': False,
        'touches_public_api': False,
        'touches_entrypoints': False,
        'touches_packaging': False,
        'touches_structured_config': False,
        'touches_gui': bool((risk_summary or {}).get('touches_ui', False)),
        'touches_runtime_core': False,
        'touches_safe_text_only': False,
    }
    if not files:
        return flags
    safe_text_only = True
    for item in list(files or []):
        path = Path(str(item))
        suffix = path.suffix.lower()
        lowered = path.as_posix().lower()
        if suffix == '.py':
            flags['touches_python'] = True
        if _touches_public_api(path):
            flags['touches_public_api'] = True
        if _touches_entrypoint(path):
            flags['touches_entrypoints'] = True
        if path.name.lower() in _PACKAGING_NAMES:
            flags['touches_packaging'] = True
        if suffix in {'.json', '.yaml', '.yml', '.toml'}:
            flags['touches_structured_config'] = True
        if any(token in lowered for token in _GUI_HINTS):
            flags['touches_gui'] = True
        if any(token in lowered for token in _RUNTIME_HINTS):
            flags['touches_runtime_core'] = True
        if suffix not in _SAFE_TEXT_SUFFIXES:
            safe_text_only = False
    flags['touches_safe_text_only'] = bool(safe_text_only and not flags['touches_python'] and not flags['touches_structured_config'])
    flags['touches_packaging'] = flags['touches_packaging'] or _touches_packaging(files, risk_summary)
    return flags


def compute_verification_policy(risk_summary: dict[str, Any], target_files: list[str]) -> dict[str, Any]:
    files = [str(item) for item in list(target_files or []) if str(item)]
    flags = _surface_flags(files, risk_summary)
    required: list[str] = []
    packs: list[str] = []
    reason_codes: list[str] = []
    floor = 'none'

    for item in files:
        path = Path(item)
        suffix = path.suffix.lower()
        name = path.name.lower()
        if suffix == '.py':
            required.extend(['python-parse', 'python-compile-smoke', 'python-import-smoke'])
            packs.append('python-runtime')
            floor = _raise_floor(floor, 'runtime')
            if _touches_public_api(path):
                required.append('export-contract')
                packs.append('python-public-api')
                reason_codes.append(f'public_api:{path.as_posix()}')
            if _touches_entrypoint(path):
                required.append('python-boot-smoke')
                packs.append('entrypoint-boot')
                reason_codes.append(f'entrypoint:{path.as_posix()}')
        elif suffix == '.json':
            required.append('json-parse')
            packs.append('config-structured')
            floor = _raise_floor(floor, 'syntax')
        elif suffix in {'.yaml', '.yml'}:
            required.append('yaml-parse')
            packs.append('config-structured')
            floor = _raise_floor(floor, 'syntax')
        elif suffix == '.toml':
            required.append('toml-parse')
            packs.append('config-structured')
            floor = _raise_floor(floor, 'syntax')
            if name in _PACKAGING_NAMES:
                required.append('build')
                packs.append('packaging')
                floor = _raise_floor(floor, 'runtime')
                reason_codes.append(f'packaging:{path.as_posix()}')
        elif suffix in {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'}:
            required.append('typescript-parse')
            floor = _raise_floor(floor, 'syntax')
            if any(token in path.as_posix().lower() for token in _GUI_HINTS):
                packs.append('gui-smoke')
                reason_codes.append(f'gui_surface:{path.as_posix()}')

    risk_level = str((risk_summary or {}).get('risk_level') or 'low').lower()
    if risk_level in {'medium', 'high', 'critical'} and flags['touches_safe_text_only']:
        floor = _raise_floor(floor, 'syntax')
    if risk_level in {'medium', 'high', 'critical'} and (flags['touches_python'] or flags['touches_packaging'] or flags['touches_runtime_core']):
        floor = _raise_floor(floor, 'runtime')
    if risk_level in {'high', 'critical'} and (flags['touches_public_api'] or flags['touches_entrypoints']):
        floor = _raise_floor(floor, 'runtime')
        reason_codes.append('high_risk_python_surface')

    allow_no_verifiers = bool(flags['touches_safe_text_only'] and floor == 'none' and risk_level == 'low')
    if allow_no_verifiers:
        reason_codes.append('safe_text_only_low_risk')

    policy = VerificationPolicy(
        required_verifiers=_dedupe(required),
        verification_floor=floor,
        packs=_dedupe(packs),
        reason_codes=_dedupe(reason_codes),
        surface_flags=flags,
        allow_applied_no_verifiers=allow_no_verifiers,
    )
    return policy.to_dict()


def compute_required_verifiers(risk_summary: dict[str, Any], target_files: list[str]) -> list[str]:
    return list(compute_verification_policy(risk_summary, target_files).get('required_verifiers') or [])


def assess_verification_outcome(risk_summary: dict[str, Any], target_files: list[str], verifier_results: list[dict[str, Any]]) -> dict[str, Any]:
    policy = compute_verification_policy(risk_summary, target_files)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in list(verifier_results or []):
        if not isinstance(item, dict):
            continue
        verifier_id = str(item.get('verifier_id') or '').strip()
        if not verifier_id:
            continue
        grouped.setdefault(verifier_id, []).append(item)

    required = list(policy.get('required_verifiers') or [])
    missing: list[str] = []
    failed: list[str] = []
    passed: list[str] = []
    for verifier_id in required:
        rows = grouped.get(verifier_id) or []
        if not rows:
            missing.append(verifier_id)
            continue
        if all(bool(row.get('ok', False)) for row in rows):
            passed.append(verifier_id)
        else:
            failed.append(verifier_id)

    floor = str(policy.get('verification_floor') or 'none')
    allow_no_verifiers = bool(policy.get('allow_applied_no_verifiers', False))
    passed_overall = not missing and not failed and (bool(required) or allow_no_verifiers or floor == 'none')
    recommended_outcome = 'verified' if passed_overall else 'applied-no-verifiers' if not required and allow_no_verifiers else 'verification-failed'
    return {
        'required_verifiers': required,
        'provided_verifiers': sorted(grouped),
        'missing_required_verifiers': missing,
        'failed_required_verifiers': failed,
        'passed_required_verifiers': passed,
        'verification_floor': floor,
        'allow_applied_no_verifiers': allow_no_verifiers,
        'policy': policy,
        'passed': passed_overall,
        'recommended_outcome': recommended_outcome,
    }
