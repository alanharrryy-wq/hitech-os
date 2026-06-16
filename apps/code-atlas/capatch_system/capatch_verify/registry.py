#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Builtin verifier registry aligned to the hardened Phase 1 policy."""

from collections import OrderedDict
from typing import Any, Callable

from .builtin_build import run_build
from .builtin_command import run_command_exit_zero
from .builtin_css import run_css_sanity
from .builtin_css_module import run_css_module_sanity
from .builtin_react_css import run_react_css_link
from .builtin_visual_static import run_visual_static_gates
from .builtin_git import run_git_clean
from .builtin_json import run_json_parse
from .builtin_python import (
    run_export_contract,
    run_python_boot_smoke,
    run_python_compile_smoke,
    run_python_import_smoke,
    run_python_parse,
)
from .builtin_tests import run_tests
from .builtin_toml import run_toml_parse
from .builtin_typescript import run_typescript_parse
from .builtin_yaml import run_yaml_parse
from .base import utc_now_iso

VerifierCallable = Callable[[list[str], dict[str, Any]], list[dict[str, Any]]]


class BuiltinVerifierRegistry:
    def __init__(self) -> None:
        self._items: 'OrderedDict[str, VerifierCallable]' = OrderedDict()

    def register(self, verifier_id: str, func: VerifierCallable) -> None:
        self._items[str(verifier_id)] = func

    def run(self, verifier_id: str, target_files: list[str], ctx: dict[str, Any]) -> list[dict[str, Any]]:
        func = self._items.get(str(verifier_id))
        if func is None:
            return [
                {
                    'verifier_id': str(verifier_id),
                    'ok': False,
                    'title': f'Unknown verifier: {verifier_id}',
                    'detail': 'No builtin verifier is registered for this verifier_id.',
                    'source_plugin': 'capatch_verify',
                    'checked_at': utc_now_iso(),
                    'evidence_refs': [],
                    'metrics': {},
                    'severity_if_failed': 'error',
                    'verification_class': 'builtin',
                }
            ]
        rows = func(list(target_files or []), dict(ctx or {}))
        normalized: list[dict[str, Any]] = []
        for row in list(rows or []):
            payload = dict(row or {})
            payload.setdefault('verifier_id', str(verifier_id))
            payload.setdefault('source_plugin', 'capatch_verify')
            payload.setdefault('checked_at', utc_now_iso())
            payload.setdefault('evidence_refs', [])
            payload.setdefault('metrics', {})
            payload.setdefault('severity_if_failed', 'error')
            payload.setdefault('verification_class', 'builtin')
            normalized.append(payload)
        return normalized


_REGISTRY = BuiltinVerifierRegistry()


def register_builtin_verifiers(registry: Any) -> None:
    target = registry if hasattr(registry, 'register') else _REGISTRY
    target.register('python-parse', run_python_parse)
    target.register('python-compile-smoke', run_python_compile_smoke)
    target.register('python-import-smoke', run_python_import_smoke)
    target.register('python-boot-smoke', run_python_boot_smoke)
    target.register('export-contract', run_export_contract)
    target.register('json-parse', run_json_parse)
    target.register('yaml-parse', run_yaml_parse)
    target.register('toml-parse', run_toml_parse)
    target.register('css-sanity', run_css_sanity)
    target.register('visual-static-gates', run_visual_static_gates)
    target.register('react-css-link', run_react_css_link)
    target.register('css-module-sanity', run_css_module_sanity)
    target.register('typescript-parse', run_typescript_parse)
    target.register('command-exit-zero', run_command_exit_zero)
    target.register('git-clean', run_git_clean)
    target.register('build', run_build)
    target.register('tests', run_tests)


def run_required_verifiers(target_files: list[str], required_verifiers: list[str], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    register_builtin_verifiers(_REGISTRY)
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for verifier_id in list(required_verifiers or []):
        for item in _REGISTRY.run(str(verifier_id), target_files, ctx):
            token = (
                str(item.get('verifier_id') or verifier_id),
                str(item.get('metrics', {}).get('file') or item.get('detail') or ''),
                str(item.get('title') or ''),
            )
            if token in seen:
                continue
            seen.add(token)
            rows.append(item)
    return rows
