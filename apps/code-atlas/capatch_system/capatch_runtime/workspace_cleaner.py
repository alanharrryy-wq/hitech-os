from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path
from typing import Any

WORKSPACE_ROOT_NAME = '.capatch'
PATCH_BACKUP_DIR = '.capatch/backups/patches'
CLEANUP_REPORT_DIR = '.capatch/artifacts/cleanup'
DEFAULT_POLICY = {
    'startup_enabled': True,
    'shutdown_enabled': True,
    'purge_pycache': True,
    'purge_tmp_days': 1,
    'purge_cache_days': 3,
    'purge_cleanup_reports_days': 14,
    'max_plugin_log_mb': 5,
    'keep_plugin_log_files': 10,
}


def _now() -> float:
    return time.time()


def _age_days(path: Path, *, now: float) -> float:
    try:
        return max(0.0, (now - path.stat().st_mtime) / 86400.0)
    except FileNotFoundError:
        return 0.0


def _ensure_dir(path: Path, *, dry_run: bool) -> None:
    if dry_run:
        return
    path.mkdir(parents=True, exist_ok=True)


def _safe_unlink(path: Path, *, dry_run: bool) -> None:
    if dry_run:
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path, ignore_errors=True)
    else:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def _list_paths(root: Path, name: str) -> list[Path]:
    return [path for path in root.rglob(name) if WORKSPACE_ROOT_NAME not in path.parts]


def _write_json(path: Path, payload: dict[str, Any], *, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='')


def _merge_policy(custom: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    for key, value in dict(custom or {}).items():
        if key in merged:
            merged[key] = value
    return merged


def policy_path(base_dir: Path) -> Path:
    return base_dir / WORKSPACE_ROOT_NAME / 'config' / 'workspace_cleaner_policy.json'


def cleanup_report_dir(base_dir: Path) -> Path:
    return base_dir / CLEANUP_REPORT_DIR


def patch_backup_dir(base_dir: Path) -> Path:
    return base_dir / PATCH_BACKUP_DIR


def load_workspace_cleaner_policy(base_dir: Path) -> dict[str, Any]:
    base_dir = Path(base_dir).resolve()
    path = policy_path(base_dir)
    if path.exists():
        try:
            return _merge_policy(json.loads(path.read_text(encoding='utf-8')))
        except Exception:
            return dict(DEFAULT_POLICY)
    policy = dict(DEFAULT_POLICY)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(policy, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='')
    return policy


def ensure_workspace_layout(base_dir: Path, *, dry_run: bool = False) -> list[str]:
    base_dir = Path(base_dir).resolve()
    created: list[str] = []
    for relative in [
        '.capatch',
        '.capatch/config',
        '.capatch/artifacts',
        '.capatch/artifacts/cleanup',
        '.capatch/backups',
        '.capatch/backups/patches',
        '.capatch/cache',
        '.capatch/logs',
        '.capatch/state',
        '.capatch/tmp',
    ]:
        path = base_dir / relative
        if not path.exists():
            created.append(relative)
        _ensure_dir(path, dry_run=dry_run)
    return created


def migrate_legacy_patch_backups(base_dir: Path, *, dry_run: bool = False) -> dict[str, Any]:
    base_dir = Path(base_dir).resolve()
    legacy_dir = base_dir / '_chatgpt_patch_backups'
    canonical_dir = patch_backup_dir(base_dir)
    moved: list[str] = []
    collisions: list[str] = []
    ensure_workspace_layout(base_dir, dry_run=dry_run)
    if not legacy_dir.exists() or legacy_dir.resolve() == canonical_dir.resolve():
        return {'legacy_exists': legacy_dir.exists(), 'moved': moved, 'collisions': collisions, 'canonical_dir': str(canonical_dir)}
    for child in sorted(legacy_dir.iterdir(), key=lambda p: p.name):
        destination = canonical_dir / child.name
        if destination.exists():
            collisions.append(child.name)
            continue
        moved.append(child.name)
        if not dry_run:
            shutil.move(str(child), str(destination))
    if legacy_dir.exists() and not any(legacy_dir.iterdir()):
        readme = legacy_dir / 'README.txt'
        if not dry_run:
            legacy_dir.mkdir(parents=True, exist_ok=True)
            readme.write_text(
                'Legacy backup dir migrated. Canonical patch backups now live at .capatch/backups/patches.\n',
                encoding='utf-8',
                newline='',
            )
    return {'legacy_exists': legacy_dir.exists(), 'moved': moved, 'collisions': collisions, 'canonical_dir': str(canonical_dir)}


def purge_pycache(base_dir: Path, *, dry_run: bool = False) -> list[str]:
    removed: list[str] = []
    for path in _list_paths(Path(base_dir).resolve(), '__pycache__'):
        removed.append(str(path.relative_to(base_dir)))
        _safe_unlink(path, dry_run=dry_run)
    return removed


def prune_old_files(target_dir: Path, *, max_age_days: int, dry_run: bool = False) -> list[str]:
    if max_age_days < 0 or not target_dir.exists():
        return []
    removed: list[str] = []
    now = _now()
    for path in sorted(target_dir.rglob('*')):
        if path.is_dir():
            continue
        if _age_days(path, now=now) < float(max_age_days):
            continue
        removed.append(str(path.relative_to(target_dir.parent.parent if target_dir.name in {'tmp', 'cache'} else target_dir.parent)))
        _safe_unlink(path, dry_run=dry_run)
    return removed


def rotate_plugin_logs(base_dir: Path, *, max_mb: int, keep_files: int, dry_run: bool = False) -> dict[str, Any]:
    log_dir = Path(base_dir).resolve() / 'capatch_plugins' / '_logs'
    oversized: list[str] = []
    trimmed: list[str] = []
    if not log_dir.exists():
        return {'oversized': oversized, 'trimmed': trimmed}
    files = sorted([path for path in log_dir.iterdir() if path.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
    max_bytes = max(1, int(max_mb)) * 1024 * 1024
    for index, path in enumerate(files):
        if index >= max(1, int(keep_files)):
            trimmed.append(path.name)
            _safe_unlink(path, dry_run=dry_run)
            continue
        if path.stat().st_size > max_bytes:
            oversized.append(path.name)
            if not dry_run:
                text = path.read_text(encoding='utf-8', errors='ignore')[-max_bytes:]
                path.write_text(text, encoding='utf-8', newline='')
    return {'oversized': oversized, 'trimmed': trimmed}


def _cleanup_report(base_dir: Path, phase: str, payload: dict[str, Any], *, dry_run: bool = False) -> Path:
    report_dir = cleanup_report_dir(base_dir)
    _ensure_dir(report_dir, dry_run=dry_run)
    target = report_dir / f'{phase}_last_cleanup.json'
    _write_json(target, payload, dry_run=dry_run)
    return target


def run_startup_cleaner(base_dir: Path, *, policy: dict[str, Any] | None = None, dry_run: bool = False) -> dict[str, Any]:
    base_dir = Path(base_dir).resolve()
    policy = _merge_policy(policy)
    payload = {
        'phase': 'startup',
        'status': 'skipped' if not policy.get('startup_enabled', True) else 'ok',
        'workspace_root': str(base_dir),
        'created_dirs': [],
        'pycache_removed': [],
        'legacy_backup_migration': {},
        'tmp_removed': [],
        'cache_removed': [],
        'plugin_logs': {},
        'dry_run': bool(dry_run),
    }
    if payload['status'] == 'skipped':
        payload['report_path'] = str(_cleanup_report(base_dir, 'startup', payload, dry_run=dry_run))
        return payload
    payload['created_dirs'] = ensure_workspace_layout(base_dir, dry_run=dry_run)
    if policy.get('purge_pycache', True):
        payload['pycache_removed'] = purge_pycache(base_dir, dry_run=dry_run)
    payload['legacy_backup_migration'] = migrate_legacy_patch_backups(base_dir, dry_run=dry_run)
    payload['tmp_removed'] = prune_old_files(base_dir / 'tmp', max_age_days=int(policy.get('purge_tmp_days', 1)), dry_run=dry_run)
    payload['cache_removed'] = prune_old_files(base_dir / 'reports' / 'cache', max_age_days=int(policy.get('purge_cache_days', 3)), dry_run=dry_run)
    payload['plugin_logs'] = rotate_plugin_logs(
        base_dir,
        max_mb=int(policy.get('max_plugin_log_mb', 5)),
        keep_files=int(policy.get('keep_plugin_log_files', 10)),
        dry_run=dry_run,
    )
    payload['report_path'] = str(_cleanup_report(base_dir, 'startup', payload, dry_run=dry_run))
    return payload


def run_shutdown_cleaner(
    base_dir: Path,
    *,
    policy: dict[str, Any] | None = None,
    dry_run: bool = False,
    run_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    base_dir = Path(base_dir).resolve()
    policy = _merge_policy(policy)
    payload = {
        'phase': 'shutdown',
        'status': 'skipped' if not policy.get('shutdown_enabled', True) else 'ok',
        'workspace_root': str(base_dir),
        'cleanup_reports_removed': [],
        'plugin_logs': {},
        'run_summary': dict(run_summary or {}),
        'dry_run': bool(dry_run),
    }
    if payload['status'] == 'skipped':
        payload['report_path'] = str(_cleanup_report(base_dir, 'shutdown', payload, dry_run=dry_run))
        return payload
    ensure_workspace_layout(base_dir, dry_run=dry_run)
    payload['cleanup_reports_removed'] = prune_old_files(
        cleanup_report_dir(base_dir),
        max_age_days=int(policy.get('purge_cleanup_reports_days', 14)),
        dry_run=dry_run,
    )
    payload['plugin_logs'] = rotate_plugin_logs(
        base_dir,
        max_mb=int(policy.get('max_plugin_log_mb', 5)),
        keep_files=int(policy.get('keep_plugin_log_files', 10)),
        dry_run=dry_run,
    )
    payload['report_path'] = str(_cleanup_report(base_dir, 'shutdown', payload, dry_run=dry_run))
    return payload
