#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Helpers for the Autofix Bridge front.

This module stays intentionally stdlib-only and plugin-friendly.
It provides:
- FixProposalV2 builder
- evidence/signal extraction
- applicability predicate evaluation
- safe command allowlist checks
- rollback/verification recipe helpers
"""

import os
import re
import shlex
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

FIX_PROPOSAL_SCHEMA_VERSION = '2.0.0'
DEFAULT_MAX_FIXES = 2

NODE_MANIFESTS = ('package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock')
PYTHON_MANIFESTS = ('requirements.txt', 'requirements-dev.txt', 'pyproject.toml', 'setup.cfg')
CONFIG_CANDIDATES = (
    '.env',
    '.env.local',
    '.env.development',
    'config.json',
    'settings.json',
    'appsettings.json',
    'config.yaml',
    'config.yml',
    'settings.yaml',
    'settings.yml',
    'config.toml',
    'settings.toml',
    'docker-compose.yml',
    'docker-compose.yaml',
)

PORT_SIGNAL_TERMS = [
    'eaddrinuse',
    'address already in use',
    'port already in use',
    'bind failed',
    'port conflict',
]
NODE_SIGNAL_TERMS = [
    'cannot find module',
    'module not found',
    'err_module_not_found',
    'missing dependency',
    'npm err',
    'node_modules',
]
PYTHON_SIGNAL_TERMS = [
    'modulenotfounderror',
    'no module named',
    'venv',
    'virtualenv',
    'site-packages',
    'pip install',
]
DB_SIGNAL_TERMS = [
    'connection refused',
    'database is locked',
    'too many connections',
    'econnreset',
    'could not connect',
    'db reconnect',
    'retry',
]
CONFIG_SIGNAL_TERMS = [
    'config',
    'yaml',
    'json',
    'toml',
    'env',
    'invalid configuration',
    'missing key',
    'unexpected token',
]
TEXTUAL_CONFIG_SIGNAL_TERMS = [
    'invalid config',
    'missing key',
    'unknown option',
    'bad config',
    'malformed',
]


@dataclass(slots=True)
class PredicateEvaluation:
    type: str
    ok: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {'type': self.type, 'ok': self.ok, 'detail': self.detail}


@dataclass(slots=True)
class FixProposalV2:
    proposal_id: str
    title: str
    rationale: str
    family: str
    affected_paths: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    ops_payload: list[dict[str, Any]] = field(default_factory=list)
    risk_level: str = 'low'
    reversible: bool = True
    source_plugin: str = 'fixer.autofix-bridge'
    metadata: dict[str, Any] = field(default_factory=dict)
    applicability_predicates: list[dict[str, Any]] = field(default_factory=list)
    rollback_recipe: list[dict[str, Any]] = field(default_factory=list)
    verification_recipe: list[dict[str, Any]] = field(default_factory=list)
    verification_steps: list[str] = field(default_factory=list)
    confidence_reason: str = ''

    def to_session_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.setdefault('metadata', {})
        payload['metadata'] = dict(payload['metadata'])
        payload['metadata'].setdefault('fix_schema_version', FIX_PROPOSAL_SCHEMA_VERSION)
        payload['metadata'].setdefault('family', self.family)
        payload['risk_tier'] = 'safe' if self.risk_level == 'low' and self.reversible else 'guarded'
        if self.risk_level in {'high', 'critical'}:
            payload['risk_tier'] = 'high-risk'
        payload['confidence_score'] = payload['metadata'].get('confidence_score', 0.66 if payload['risk_tier'] == 'safe' else 0.51)
        payload['evidence_count'] = len(payload['metadata'].get('evidence_refs', []) or [])
        payload['cross_signal_support'] = list(payload['metadata'].get('cross_signal_support', []) or [])
        payload['contradictions'] = list(payload['metadata'].get('contradictions', []) or [])
        return payload



def normalize_relpath(root_dir: Path, candidate: Path | str) -> str:
    path = Path(candidate)
    if not path.is_absolute():
        path = (Path(root_dir) / path).resolve()
    try:
        return path.relative_to(Path(root_dir).resolve()).as_posix()
    except Exception:
        return path.as_posix()



def file_exists_any(root_dir: Path, candidates: list[str]) -> str | None:
    for item in candidates:
        path = Path(root_dir) / item
        if path.exists():
            return item.replace('\\', '/')
    return None



def detect_package_manager(root_dir: Path) -> str:
    root_dir = Path(root_dir)
    if (root_dir / 'pnpm-lock.yaml').exists():
        return 'pnpm'
    if (root_dir / 'yarn.lock').exists():
        return 'yarn'
    return 'npm'



def _safe_read(path_value: Path) -> str:
    try:
        return path_value.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''



def collect_signal_text(*, artifacts: list[Any], findings: list[Any], recommendations: list[Any] | None = None) -> str:
    parts: list[str] = []
    for item in list(artifacts or []):
        excerpt = getattr(item, 'excerpt', None)
        summary = getattr(item, 'summary', None)
        metadata = getattr(item, 'metadata', None)
        if excerpt:
            parts.append(str(excerpt))
        if summary:
            parts.append(str(summary))
        if isinstance(metadata, dict):
            parts.append(str(metadata))
    for item in list(findings or []):
        parts.append(str(getattr(item, 'title', '') or ''))
        parts.append(str(getattr(item, 'detail', '') or ''))
        parts.extend(str(tag) for tag in list(getattr(item, 'tags', []) or []))
    for item in list(recommendations or []):
        parts.append(str(getattr(item, 'title', '') or ''))
        parts.append(str(getattr(item, 'rationale', '') or ''))
    return '\n'.join(parts).lower()



def signal_contains(text: str, terms: list[str]) -> bool:
    haystack = str(text or '').lower()
    return any(str(term).lower() in haystack for term in list(terms or []))



def find_candidate_config(root_dir: Path) -> str | None:
    return file_exists_any(root_dir, list(CONFIG_CANDIDATES))



def extract_port(text: str, default: int = 3000) -> int:
    patterns = [
        r'port\s+(\d{2,5})',
        r':(\d{2,5})',
        r'listen(?:ing)?\s+on\s+(\d{2,5})',
    ]
    for pattern in patterns:
        match = re.search(pattern, str(text or '').lower())
        if match:
            try:
                value = int(match.group(1))
                if 1 <= value <= 65535:
                    return value
            except Exception:
                continue
    return default



def next_port(port_value: int) -> int:
    return 3001 if port_value >= 65535 else max(1024, int(port_value) + 1)



def build_restore_recipe(paths: list[str], *, family: str, delete_paths: list[str] | None = None) -> list[dict[str, Any]]:
    recipe: list[dict[str, Any]] = []
    unique_paths = []
    seen = set()
    for item in list(paths or []):
        key = str(item).replace('\\', '/')
        if not key or key in seen:
            continue
        seen.add(key)
        unique_paths.append(key)
    if unique_paths:
        recipe.append({'action': 'restore_paths', 'paths': unique_paths, 'family': family})
    if delete_paths:
        recipe.append({'action': 'delete_paths', 'paths': [str(item).replace('\\', '/') for item in delete_paths], 'family': family})
    return recipe



def build_verification_recipe(paths: list[str], *, family: str, extra: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    recipe: list[dict[str, Any]] = []
    for item in list(paths or []):
        suffix = Path(item).suffix.lower()
        if suffix == '.py':
            recipe.append({'kind': 'builtin-verifier', 'verifier_id': 'python-parse', 'path': item, 'family': family})
            recipe.append({'kind': 'builtin-verifier', 'verifier_id': 'python-compile-smoke', 'path': item, 'family': family})
            recipe.append({'kind': 'builtin-verifier', 'verifier_id': 'python-import-smoke', 'path': item, 'family': family})
            lowered = Path(item).as_posix().lower()
            if Path(item).name.lower() in {'__main__.py', 'main.py', 'cli.py', 'app.py', 'bootstrap.py', 'entrypoint.py'} or any(token in lowered for token in ('bootstrap', 'entrypoint', 'runtime', 'launch', 'startup')):
                recipe.append({'kind': 'builtin-verifier', 'verifier_id': 'python-boot-smoke', 'path': item, 'family': family})
        elif suffix == '.json':
            recipe.append({'kind': 'builtin-verifier', 'verifier_id': 'json-parse', 'path': item, 'family': family})
        elif suffix in {'.yaml', '.yml'}:
            recipe.append({'kind': 'builtin-verifier', 'verifier_id': 'yaml-parse', 'path': item, 'family': family})
        elif suffix == '.toml':
            recipe.append({'kind': 'builtin-verifier', 'verifier_id': 'toml-parse', 'path': item, 'family': family})
        elif suffix in {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'}:
            recipe.append({'kind': 'builtin-verifier', 'verifier_id': 'typescript-parse', 'path': item, 'family': family})
    if extra:
        recipe.extend(list(extra))
    return recipe



def build_fix_proposal_v2(**kwargs: Any) -> dict[str, Any]:
    return FixProposalV2(**kwargs).to_session_payload()



def _predicate_signal_contains(text: str, predicate: dict[str, Any]) -> PredicateEvaluation:
    terms = [str(item) for item in list(predicate.get('terms') or []) if str(item)]
    ok = signal_contains(text, terms)
    return PredicateEvaluation('signal_contains', ok, f'terms={terms}')



def _predicate_any_file_exists(root_dir: Path, predicate: dict[str, Any]) -> PredicateEvaluation:
    paths = [str(item) for item in list(predicate.get('paths') or []) if str(item)]
    found = file_exists_any(root_dir, paths)
    return PredicateEvaluation('any_file_exists', bool(found), f'found={found!r} candidates={paths}')



def _predicate_file_text_contains(root_dir: Path, predicate: dict[str, Any]) -> PredicateEvaluation:
    path_value = str(predicate.get('path') or '').replace('\\', '/')
    terms = [str(item) for item in list(predicate.get('terms') or []) if str(item)]
    text = _safe_read(Path(root_dir) / path_value)
    ok = bool(text) and signal_contains(text, terms)
    return PredicateEvaluation('file_text_contains', ok, f'path={path_value!r} terms={terms}')



def _predicate_finding_tag_present(findings: list[Any], predicate: dict[str, Any]) -> PredicateEvaluation:
    wanted = {str(item).strip().lower() for item in list(predicate.get('tags') or []) if str(item).strip()}
    observed = set()
    for finding in list(findings or []):
        observed.update(str(tag).strip().lower() for tag in list(getattr(finding, 'tags', []) or []) if str(tag).strip())
    ok = bool(wanted.intersection(observed))
    return PredicateEvaluation('finding_tag_present', ok, f'wanted={sorted(wanted)} observed={sorted(observed)[:12]}')



def _predicate_session_mode(session: Any, predicate: dict[str, Any]) -> PredicateEvaluation:
    modes = {str(item).strip() for item in list(predicate.get('modes') or []) if str(item).strip()}
    current = str(getattr(session, 'execution_mode', '') or '')
    ok = current in modes if modes else True
    return PredicateEvaluation('session_mode', ok, f'current={current!r} modes={sorted(modes)}')



def evaluate_applicability_predicates(root_dir: Path, session: Any, predicates: list[dict[str, Any]]) -> tuple[bool, list[dict[str, Any]]]:
    root_dir = Path(root_dir).resolve()
    signal_text = collect_signal_text(
        artifacts=list(getattr(session, 'artifacts', []) or []),
        findings=list(getattr(session, 'findings', []) or []),
        recommendations=list(getattr(session, 'recommendations', []) or []),
    )
    evaluations: list[PredicateEvaluation] = []
    for predicate in list(predicates or []):
        kind = str(predicate.get('type') or '').strip().lower()
        if kind == 'signal_contains':
            evaluations.append(_predicate_signal_contains(signal_text, predicate))
        elif kind == 'any_file_exists':
            evaluations.append(_predicate_any_file_exists(root_dir, predicate))
        elif kind == 'file_text_contains':
            evaluations.append(_predicate_file_text_contains(root_dir, predicate))
        elif kind == 'finding_tag_present':
            evaluations.append(_predicate_finding_tag_present(list(getattr(session, 'findings', []) or []), predicate))
        elif kind == 'session_mode':
            evaluations.append(_predicate_session_mode(session, predicate))
        else:
            evaluations.append(PredicateEvaluation(kind or 'unknown', False, 'predicate type unsupported'))
    ok = bool(evaluations) and all(item.ok for item in evaluations)
    return ok, [item.to_dict() for item in evaluations]



def parse_command(command: str) -> list[str]:
    return shlex.split(str(command), posix=(os.name != 'nt'))



def _is_python_token(token: str) -> bool:
    lowered = str(token or '').strip().lower()
    return lowered in {'python', 'python3', 'py'} or lowered.endswith('python.exe') or lowered.endswith('/python')



def command_is_allowlisted(command: str, *, family: str) -> tuple[bool, str]:
    argv = parse_command(command)
    if not argv:
        return False, 'empty command'
    head = argv[0].lower()
    lowered = [item.lower() for item in argv]

    if family == 'node-deps':
        if head not in {'npm', 'pnpm', 'yarn'}:
            return False, f'node-deps only allows npm/pnpm/yarn, got {head!r}'
        joined = ' '.join(lowered)
        if head == 'npm' and 'install' in lowered and '--ignore-scripts' in lowered:
            return True, joined
        if head == 'pnpm' and 'install' in lowered and '--ignore-scripts' in lowered:
            return True, joined
        if head == 'yarn' and 'install' in lowered and '--ignore-scripts' in lowered:
            return True, joined
        return False, f'node-deps command not allowlisted: {argv}'

    if family == 'python-venv':
        if _is_python_token(argv[0]) and lowered[1:3] == ['-m', 'venv']:
            return True, 'python -m venv'
        if _is_python_token(argv[0]) and lowered[1:3] == ['-m', 'pip'] and 'install' in lowered:
            return True, 'python -m pip install'
        return False, f'python-venv command not allowlisted: {argv}'

    return False, f'family {family!r} does not allow commands'



def verifier_ctx_defaults(root_dir: Path, proposal: Any) -> dict[str, Any]:
    meta = dict(getattr(proposal, 'metadata', {}) or {}) if not isinstance(proposal, dict) else dict(proposal.get('metadata', {}) or {})
    ctx = {
        'root_dir': str(Path(root_dir).resolve()),
        'build_command': meta.get('build_command'),
        'test_command': meta.get('test_command'),
    }
    return ctx



def relative_candidate_paths(root_dir: Path, *paths: str) -> list[str]:
    rows: list[str] = []
    for item in paths:
        if not item:
            continue
        path_value = Path(root_dir) / item
        if path_value.exists():
            rows.append(normalize_relpath(root_dir, path_value))
    return rows



def runtime_python_command() -> str:
    executable = Path(sys.executable or 'python')
    return executable.name if executable.name else 'python'
