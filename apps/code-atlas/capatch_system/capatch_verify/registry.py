#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Builtin verifier registry aligned to the Phase 0 master spec."""

from collections import OrderedDict
from typing import Any, Callable

from .builtin_build import run_build
from .builtin_git import run_git_clean
from .builtin_json import run_json_parse
from .builtin_python import run_export_contract, run_python_import_smoke, run_python_parse
from .builtin_tests import run_tests
from .builtin_toml import run_toml_parse
from .builtin_typescript import run_typescript_parse
from .builtin_yaml import run_yaml_parse

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
                    'evidence_refs': [],
                    'metrics': {},
                    'severity_if_failed': 'error',
                    'verification_class': 'builtin',
                }
            ]
        return func(target_files, ctx)


_REGISTRY = BuiltinVerifierRegistry()


def register_builtin_verifiers(registry: Any) -> None:
    target = registry if hasattr(registry, 'register') else _REGISTRY
    target.register('python-parse', run_python_parse)
    target.register('python-import-smoke', run_python_import_smoke)
    target.register('export-contract', run_export_contract)
    target.register('json-parse', run_json_parse)
    target.register('yaml-parse', run_yaml_parse)
    target.register('toml-parse', run_toml_parse)
    target.register('typescript-parse', run_typescript_parse)
    target.register('git-clean', run_git_clean)
    target.register('build', run_build)
    target.register('tests', run_tests)


def run_required_verifiers(target_files: list[str], required_verifiers: list[str], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    if not _REGISTRY._items:
        register_builtin_verifiers(_REGISTRY)
    rows: list[dict[str, Any]] = []
    for verifier_id in list(required_verifiers or []):
        rows.extend(_REGISTRY.run(str(verifier_id), list(target_files or []), dict(ctx or {})))
    return rows
