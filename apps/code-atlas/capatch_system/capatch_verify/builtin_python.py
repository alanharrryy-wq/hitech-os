#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import ast
import json
import os
import py_compile
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Any

from .base import VerifierResultRow, existing_target_files

_RUNTIME_PROBE = r"""
from __future__ import annotations
import importlib
import importlib.util
import json
import os
import sys
import time
import traceback
from pathlib import Path


def _trim(value: str, limit: int = 4000) -> str:
    text = value or ''
    return text if len(text) <= limit else text[: limit - 3] + '...'


def _derive_module_name(root_dir: Path, target_path: Path) -> str | None:
    try:
        relative = target_path.relative_to(root_dir)
    except Exception:
        return None
    parts = list(relative.parts)
    if not parts:
        return None
    if parts[-1] == '__init__.py':
        parts = parts[:-1]
    else:
        parts[-1] = Path(parts[-1]).stem
    if not parts:
        return None
    if not all(part.isidentifier() for part in parts):
        return None
    return '.'.join(parts)


def _import_by_file(target_path: Path, synthetic_name: str):
    spec = importlib.util.spec_from_file_location(synthetic_name, str(target_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to build import spec for {target_path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[synthetic_name] = module
    spec.loader.exec_module(module)
    return module


def _boot_probe(module, module_name: str | None, target_path: Path) -> tuple[bool, str | None]:
    candidates = ['main', 'cli', 'run', 'app', 'bootstrap', 'entrypoint']
    found = []
    for name in candidates:
        try:
            value = getattr(module, name)
        except Exception:
            continue
        if callable(value):
            found.append(name)
    if target_path.name == '__main__.py':
        return True, '__main__ module imported'
    if found:
        return True, f'callables={found}'
    return False, 'entrypoint callable not found'


def main() -> int:
    payload = json.loads(sys.stdin.read())
    root_dir = Path(payload['root_dir']).resolve()
    target_path = Path(payload['target_path']).resolve()
    timeout_seconds = float(payload.get('timeout_seconds') or 5.0)
    mode = str(payload.get('mode') or 'import')
    sys.path[:] = [str(root_dir)] + [item for item in sys.path if item and os.path.abspath(item) != str(root_dir)]
    module_name = _derive_module_name(root_dir, target_path)
    started = time.perf_counter()
    stdout_before = getattr(sys.stdout, 'tell', lambda: None)
    stderr_before = getattr(sys.stderr, 'tell', lambda: None)
    result = {
        'success': False,
        'mode': mode,
        'root_dir': str(root_dir),
        'target_path': str(target_path),
        'module_name': module_name,
        'import_strategy': 'module_name' if module_name else 'file_spec',
        'exception_class': None,
        'traceback_summary': None,
        'boot_probe': None,
    }
    try:
        if module_name:
            module = importlib.import_module(module_name)
        else:
            synthetic_name = f'_capatch_probe_{target_path.stem}_{abs(hash(str(target_path))) & 0xfffffff}'
            module = _import_by_file(target_path, synthetic_name)
            result['module_name'] = getattr(module, '__name__', synthetic_name)
        result['module_imported'] = getattr(module, '__name__', result['module_name'])
        if mode == 'boot':
            boot_ok, boot_detail = _boot_probe(module, result['module_name'], target_path)
            result['boot_probe'] = boot_detail
            result['success'] = bool(boot_ok)
        else:
            result['success'] = True
    except Exception as exc:
        result['success'] = False
        result['exception_class'] = type(exc).__name__
        result['traceback_summary'] = _trim(''.join(traceback.format_exception(type(exc), exc, exc.__traceback__)), 5000)
    result['elapsed_ms'] = round((time.perf_counter() - started) * 1000.0, 3)
    result['timed_out'] = bool(result['elapsed_ms'] > timeout_seconds * 1000.0)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
"""

_ENTRYPOINT_NAMES = {
    '__main__.py',
    'main.py',
    'cli.py',
    'app.py',
    'bootstrap.py',
    'entrypoint.py',
}

_ENTRYPOINT_HINTS = ('bootstrap', 'entrypoint', 'runtime', 'launch', 'startup')


def _root_dir(ctx: dict[str, object]) -> Path:
    return Path(str((ctx or {}).get('root_dir') or '.')).resolve()


def _python_targets(target_files: list[str], ctx: dict[str, object]) -> list[Path]:
    rows: list[Path] = []
    seen: set[str] = set()
    for path in existing_target_files(target_files, ctx):
        if path.suffix.lower() != '.py':
            continue
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        rows.append(path)
    return rows


def _derive_module_name(root_dir: Path, path: Path) -> str | None:
    try:
        relative = path.resolve().relative_to(root_dir)
    except Exception:
        return None
    parts = list(relative.parts)
    if not parts:
        return None
    if parts[-1] == '__init__.py':
        parts = parts[:-1]
    else:
        parts[-1] = Path(parts[-1]).stem
    if not parts:
        return None
    if not all(part.isidentifier() for part in parts):
        return None
    return '.'.join(parts)


def _is_entrypoint(path: Path) -> bool:
    lowered = path.as_posix().lower()
    if path.name.lower() in _ENTRYPOINT_NAMES:
        return True
    return any(token in lowered for token in _ENTRYPOINT_HINTS)


def _trim(value: str, limit: int = 4000) -> str:
    text = value or ''
    return text if len(text) <= limit else text[: limit - 3] + '...'


def _run_runtime_probe(mode: str, path: Path, ctx: dict[str, object]) -> dict[str, Any]:
    root_dir = _root_dir(ctx)
    timeout_seconds = float((ctx or {}).get('python_probe_timeout_seconds') or 5.0)
    payload = {
        'mode': mode,
        'root_dir': str(root_dir),
        'target_path': str(path.resolve()),
        'timeout_seconds': timeout_seconds,
    }
    started = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, '-I', '-c', _RUNTIME_PROBE],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        cwd=str(root_dir),
        env={
            'PYTHONNOUSERSITE': '1',
            'PYTHONDONTWRITEBYTECODE': '1',
            'PYTHONPATH': str(root_dir),
        },
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
    stdout_text = _trim(completed.stdout or '')
    stderr_text = _trim(completed.stderr or '')
    parsed: dict[str, Any] = {}
    if stdout_text:
        for candidate in reversed(stdout_text.splitlines()):
            line = candidate.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
                break
            except Exception:
                continue
    parsed.setdefault('mode', mode)
    parsed.setdefault('success', completed.returncode == 0)
    parsed.setdefault('elapsed_ms', elapsed_ms)
    parsed.setdefault('stdout', stdout_text)
    parsed.setdefault('stderr', stderr_text)
    parsed.setdefault('returncode', completed.returncode)
    parsed.setdefault('module_name', _derive_module_name(root_dir, path))
    parsed.setdefault('module_imported', parsed.get('module_name'))
    return parsed


def run_python_parse(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for path in _python_targets(target_files, ctx):
        try:
            ast.parse(path.read_text(encoding='utf-8', errors='replace'), filename=str(path))
            rows.append(VerifierResultRow('python-parse', True, f'Python parse OK: {path.name}', str(path), metrics={'file': str(path)}).to_dict())
        except Exception as exc:
            rows.append(VerifierResultRow('python-parse', False, f'Python parse failed: {path.name}', f'{type(exc).__name__}: {exc}', metrics={'file': str(path), 'exception_class': type(exc).__name__}).to_dict())
    return rows


def run_python_compile_smoke(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for path in _python_targets(target_files, ctx):
        try:
            py_compile.compile(str(path), doraise=True)
            rows.append(
                VerifierResultRow(
                    'python-compile-smoke',
                    True,
                    f'Python compile OK: {path.name}',
                    str(path),
                    metrics={'file': str(path), 'module_name': _derive_module_name(_root_dir(ctx), path)},
                ).to_dict()
            )
        except Exception as exc:
            rows.append(
                VerifierResultRow(
                    'python-compile-smoke',
                    False,
                    f'Python compile failed: {path.name}',
                    f'{type(exc).__name__}: {exc}',
                    metrics={'file': str(path), 'exception_class': type(exc).__name__},
                ).to_dict()
            )
    return rows


def run_python_import_smoke(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for path in _python_targets(target_files, ctx):
        try:
            probe = _run_runtime_probe('import', path, ctx)
            ok = bool(probe.get('success', False))
            detail = probe.get('traceback_summary') or probe.get('stderr') or str(path)
            rows.append(
                VerifierResultRow(
                    'python-import-smoke',
                    ok,
                    f"Python import {'OK' if ok else 'FAILED'}: {path.name}",
                    detail,
                    metrics={
                        'file': str(path),
                        'module_name': probe.get('module_name'),
                        'module_imported': probe.get('module_imported'),
                        'elapsed_ms': probe.get('elapsed_ms'),
                        'exception_class': probe.get('exception_class'),
                        'stderr': probe.get('stderr'),
                        'stdout': probe.get('stdout'),
                        'returncode': probe.get('returncode'),
                    },
                ).to_dict()
            )
        except subprocess.TimeoutExpired as exc:
            rows.append(
                VerifierResultRow(
                    'python-import-smoke',
                    False,
                    f'Python import timed out: {path.name}',
                    f'TimeoutExpired: {exc}',
                    metrics={'file': str(path), 'exception_class': 'TimeoutExpired'},
                ).to_dict()
            )
        except Exception as exc:
            rows.append(
                VerifierResultRow(
                    'python-import-smoke',
                    False,
                    f'Python import probe crashed: {path.name}',
                    f'{type(exc).__name__}: {exc}',
                    metrics={'file': str(path), 'exception_class': type(exc).__name__},
                ).to_dict()
            )
    return rows


def run_python_boot_smoke(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for path in _python_targets(target_files, ctx):
        if not _is_entrypoint(path):
            continue
        try:
            probe = _run_runtime_probe('boot', path, ctx)
            ok = bool(probe.get('success', False))
            detail = probe.get('boot_probe') or probe.get('traceback_summary') or probe.get('stderr') or str(path)
            rows.append(
                VerifierResultRow(
                    'python-boot-smoke',
                    ok,
                    f"Python boot {'OK' if ok else 'FAILED'}: {path.name}",
                    str(detail),
                    metrics={
                        'file': str(path),
                        'module_name': probe.get('module_name'),
                        'module_imported': probe.get('module_imported'),
                        'elapsed_ms': probe.get('elapsed_ms'),
                        'exception_class': probe.get('exception_class'),
                        'stderr': probe.get('stderr'),
                        'stdout': probe.get('stdout'),
                        'returncode': probe.get('returncode'),
                        'boot_probe': probe.get('boot_probe'),
                    },
                ).to_dict()
            )
        except subprocess.TimeoutExpired as exc:
            rows.append(
                VerifierResultRow(
                    'python-boot-smoke',
                    False,
                    f'Python boot timed out: {path.name}',
                    f'TimeoutExpired: {exc}',
                    metrics={'file': str(path), 'exception_class': 'TimeoutExpired'},
                ).to_dict()
            )
        except Exception as exc:
            rows.append(
                VerifierResultRow(
                    'python-boot-smoke',
                    False,
                    f'Python boot probe crashed: {path.name}',
                    f'{type(exc).__name__}: {exc}',
                    metrics={'file': str(path), 'exception_class': type(exc).__name__},
                ).to_dict()
            )
    return rows


def run_export_contract(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for path in _python_targets(target_files, ctx):
        lowered = path.as_posix().lower()
        if path.name != '__init__.py' and 'export' not in lowered:
            continue
        try:
            source = path.read_text(encoding='utf-8', errors='replace')
            tree = ast.parse(source, filename=str(path))
            exported_names = None
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == '__all__':
                            if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                                exported_names = [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)]
                            break
            detail = f'{path}' if exported_names is None else f"{path} | __all__={exported_names}"
            rows.append(VerifierResultRow('export-contract', True, f'Export contract parse OK: {path.name}', detail, metrics={'file': str(path), 'exports': exported_names}).to_dict())
        except Exception as exc:
            rows.append(VerifierResultRow('export-contract', False, f'Export contract failed: {path.name}', f'{type(exc).__name__}: {exc}', metrics={'file': str(path), 'exception_class': type(exc).__name__}).to_dict())
    return rows
