from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import socket
import sys
from pathlib import Path
from typing import Any

DEFAULT_ALLOWED_ROOT_NAMES = ("capatch_system",)


def _stable_list(values: list[str] | tuple[str, ...] | None) -> list[str]:
    rows = [str(item).strip() for item in list(values or [])]
    return [item for item in rows if item]


def _fingerprint_mapping(payload: dict[str, Any]) -> str:
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode('utf-8', errors='replace')
    return hashlib.sha256(data).hexdigest()


def _safe_resolve(path_value: Path | str | None) -> str | None:
    if path_value is None:
        return None
    try:
        return str(Path(path_value).resolve())
    except Exception:
        return str(path_value)


def _read_registry_hash(base_dir: Path) -> str | None:
    registry_path = base_dir / 'capatch_plugins' / '_plugin_registry.json'
    if not registry_path.exists():
        return None
    try:
        return hashlib.sha256(registry_path.read_bytes()).hexdigest()
    except Exception:
        return None


def detect_workspace_markers(target_path: Path) -> dict[str, bool]:
    names: set[str] = set()
    if target_path.exists() and target_path.is_dir():
        for child in list(target_path.iterdir())[:256]:
            names.add(child.name)
    elif target_path.exists():
        names.add(target_path.name)
    return {
        'has_git': '.git' in names,
        'has_package_json': 'package.json' in names,
        'has_pyproject': 'pyproject.toml' in names,
        'has_requirements': 'requirements.txt' in names,
        'has_reports_dir': 'reports' in names,
        'has_plugins_dir': 'capatch_plugins' in names,
        'has_docker_compose': any(name in names for name in ('docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml')),
        'has_dockerfile': 'Dockerfile' in names,
    }


def capture_environment_guard(
    base_dir: Path,
    target_path: Path,
    *,
    plugin_state: dict[str, Any] | None = None,
    expected_root_names: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    base_dir = Path(base_dir).resolve()
    target_path = Path(target_path).resolve()
    python_exe = Path(sys.executable).resolve()
    sys_path_rows = []
    for item in sys.path[:24]:
        try:
            sys_path_rows.append(str(Path(item).resolve()))
        except Exception:
            sys_path_rows.append(str(item))
    relevant_env = {
        'VIRTUAL_ENV': os.environ.get('VIRTUAL_ENV'),
        'PYTHONPATH': os.environ.get('PYTHONPATH'),
        'NODE_ENV': os.environ.get('NODE_ENV'),
        'CAPATCH_WINDOWS_SMOKE_REQUIRED_PLUGINS': os.environ.get('CAPATCH_WINDOWS_SMOKE_REQUIRED_PLUGINS'),
    }
    executables = {
        'python': str(python_exe),
        'git': shutil.which('git'),
        'node': shutil.which('node'),
        'npm': shutil.which('npm'),
        'pnpm': shutil.which('pnpm'),
        'yarn': shutil.which('yarn'),
    }
    plugin_runtime = {}
    if isinstance(plugin_state, dict):
        plugin_runtime = {
            'runtime_version': plugin_state.get('runtime_version'),
            'runtime_status': plugin_state.get('runtime_status'),
            'capability_map': plugin_state.get('capability_map'),
        }
    payload = {
        'cwd': _safe_resolve(Path.cwd()),
        'base_dir': str(base_dir),
        'target_path': str(target_path),
        'base_dir_name': base_dir.name,
        'target_exists': target_path.exists(),
        'target_is_dir': target_path.is_dir(),
        'hostname': socket.gethostname(),
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'python_version': platform.python_version(),
        },
        'python': {
            'executable': str(python_exe),
            'prefix': _safe_resolve(sys.prefix),
            'base_prefix': _safe_resolve(getattr(sys, 'base_prefix', sys.prefix)),
            'version_info': [sys.version_info.major, sys.version_info.minor, sys.version_info.micro],
            'venv_active': bool(os.environ.get('VIRTUAL_ENV')),
        },
        'executables': executables,
        'env_flags': relevant_env,
        'sys_path': sys_path_rows,
        'workspace_markers': detect_workspace_markers(target_path),
        'registry_hash': _read_registry_hash(base_dir),
        'plugin_runtime': plugin_runtime,
        'expected_root_names': _stable_list(expected_root_names or DEFAULT_ALLOWED_ROOT_NAMES),
    }
    payload['environment_fingerprint'] = _fingerprint_mapping({
        'base_dir': payload['base_dir'],
        'python': payload['python'],
        'executables': payload['executables'],
        'env_flags': payload['env_flags'],
        'registry_hash': payload['registry_hash'],
    })
    return payload


def evaluate_environment_guard(payload: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    warnings: list[str] = []
    severity = 'healthy'
    base_dir = str(payload.get('base_dir') or '')
    cwd = str(payload.get('cwd') or '')
    expected_root_names = set(_stable_list(payload.get('expected_root_names')))
    base_name = Path(base_dir).name if base_dir else ''
    if expected_root_names and base_name and base_name not in expected_root_names:
        warnings.append(f'unexpected_base_dir_name:{base_name}')
    target_exists = bool(payload.get('target_exists'))
    if not target_exists:
        reasons.append('target_missing')
    python = payload.get('python') if isinstance(payload.get('python'), dict) else {}
    python_exe = str(python.get('executable') or '')
    if not python_exe:
        reasons.append('python_executable_missing')
    env_flags = payload.get('env_flags') if isinstance(payload.get('env_flags'), dict) else {}
    if env_flags.get('PYTHONPATH'):
        warnings.append('pythonpath_present')
    sys_path_rows = [str(item) for item in list(payload.get('sys_path') or []) if str(item).strip()]
    if base_dir and sys_path_rows and base_dir not in sys_path_rows[:8]:
        warnings.append('base_dir_not_near_sys_path_head')
    if base_dir and cwd and Path(base_dir) != Path(cwd):
        warnings.append('cwd_differs_from_base_dir')
    registry_hash = payload.get('registry_hash')
    if registry_hash is None:
        warnings.append('registry_hash_missing')
    plugin_runtime = payload.get('plugin_runtime') if isinstance(payload.get('plugin_runtime'), dict) else {}
    runtime_status = plugin_runtime.get('runtime_status') if isinstance(plugin_runtime.get('runtime_status'), dict) else {}
    if runtime_status.get('status') in {'degraded', 'failed', 'blocked'}:
        reasons.append(f"plugin_runtime_{runtime_status.get('status')}")
    if reasons:
        severity = 'blocked'
    elif warnings:
        severity = 'degraded'
    return {
        'status': severity,
        'reasons': reasons,
        'warnings': warnings,
        'environment_fingerprint': payload.get('environment_fingerprint'),
    }
