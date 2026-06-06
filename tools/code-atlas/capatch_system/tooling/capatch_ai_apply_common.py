#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPORT_ROOT_NAME = 'capatch_ai_controlled_fix'
DEFAULT_WINDOWS_EXPORT_DIR = Path(r'F:\descargasf')
DEFAULT_REQUESTED_BY = 'alanharrryy'


@dataclass(slots=True)
class PhaseConfig:
    phase_name: str
    root_dir: Path
    export_dir: Path
    mode: str
    run_tests: bool
    checkpoint_label: str
    requested_by: str
    allow_dirty_worktree: bool = False
    skip_smoke: bool = False
    json_output: bool = False
    transaction_file: Path | None = None


@dataclass(slots=True)
class ChangePlanEntry:
    kind: str
    relative_path: str
    content: str | None = None
    notes: list[str] = field(default_factory=list)


class PhaseError(RuntimeError):
    pass


def parse_common_args(*, phase_name: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f'{phase_name} injector with dry-run, apply and rollback.')
    parser.add_argument('--root-dir', required=True, help='Ruta absoluta del repo capatch_system.')
    parser.add_argument('--export-dir', required=False, default='', help='Ruta absoluta para artefactos. En Windows usa F:\\descargasf si no se pasa.')
    parser.add_argument('--mode', required=True, choices=['dry-run', 'apply', 'rollback'], help='Modo de ejecucion.')
    parser.add_argument('--run-tests', action='store_true', help='Corre tests de scope y guarda log.')
    parser.add_argument('--checkpoint-label', default='', help='Etiqueta legible para manifest y rollback.')
    parser.add_argument('--requested-by', default=DEFAULT_REQUESTED_BY, help='Actor solicitante para auditoria.')
    parser.add_argument('--allow-dirty-worktree', action='store_true', help='Permite ejecutar aunque el repo tenga cambios locales.')
    parser.add_argument('--skip-smoke', action='store_true', help='No corre smoke/tests rapidos.')
    parser.add_argument('--json', action='store_true', help='Imprime resumen JSON final al stdout.')
    parser.add_argument('--transaction-file', default='', help='Ruta opcional a last_transaction.json para rollback.')
    return parser.parse_args()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return now_utc().isoformat().replace('+00:00', 'Z')


def safe_slug(value: str, *, fallback: str) -> str:
    raw = ''.join(ch if ch.isalnum() or ch in ('-', '_') else '-' for ch in str(value or '').strip())
    cooked = '-'.join(part for part in raw.split('-') if part)
    return cooked or fallback


def resolve_root_dir(raw: str) -> Path:
    path = Path(str(raw or '')).expanduser()
    if not path:
        raise PhaseError('root-dir vacio')
    resolved = path.resolve()
    if not resolved.exists() or not resolved.is_dir():
        raise PhaseError(f'root-dir no existe o no es carpeta: {resolved}')
    if not (resolved / 'capatch_engine').exists():
        raise PhaseError(f'root-dir no parece capatch_system: {resolved}')
    return resolved


def resolve_export_dir(raw: str, *, root_dir: Path) -> Path:
    candidate = str(raw or '').strip()
    if candidate:
        return Path(candidate).expanduser().resolve()
    if os.name == 'nt':
        return DEFAULT_WINDOWS_EXPORT_DIR
    return (root_dir / '.capatch' / 'external_audit').resolve()


def transaction_id_for(phase_name: str) -> str:
    stamp = now_utc().strftime('%Y%m%dT%H%M%SZ')
    return f'{safe_slug(phase_name, fallback="phase")}-{stamp}'


def build_phase_output_dir(*, export_dir: Path, phase_name: str, mode: str) -> Path:
    return export_dir / EXPORT_ROOT_NAME / phase_name / mode.replace('-', '_')


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding='utf-8', newline='\n')


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def relpath(path: Path, *, root_dir: Path) -> str:
    try:
        return path.resolve().relative_to(root_dir.resolve()).as_posix()
    except Exception:
        return str(path)


def snapshot_entry(path: Path, *, root_dir: Path) -> dict[str, Any]:
    exists = path.exists()
    return {
        'relative_path': relpath(path, root_dir=root_dir),
        'exists': bool(exists),
        'sha256': sha256_file(path) if exists and path.is_file() else None,
        'size_bytes': int(path.stat().st_size) if exists and path.is_file() else None,
    }


def capture_backups(paths: list[Path], *, root_dir: Path, backups_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        relative = relpath(path, root_dir=root_dir)
        backup_path = backups_dir / relative
        existed = path.exists()
        if existed and path.is_file():
            ensure_dir(backup_path.parent)
            shutil.copy2(path, backup_path)
        rows.append({
            'relative_path': relative,
            'backup_path': str(backup_path),
            'existed_before': bool(existed),
            'before_sha256': sha256_file(path) if existed and path.is_file() else None,
        })
    return rows


def restore_from_manifest(transaction: dict[str, Any]) -> dict[str, Any]:
    root_dir = Path(str(transaction.get('root_dir') or '')).expanduser().resolve()
    restored: list[str] = []
    removed: list[str] = []
    missing_backups: list[str] = []
    for item in list(transaction.get('backups') or []):
        relative = str(item.get('relative_path') or '')
        backup_path = Path(str(item.get('backup_path') or '')).expanduser()
        target = (root_dir / relative).resolve()
        existed_before = bool(item.get('existed_before', False))
        if existed_before:
            if not backup_path.exists():
                missing_backups.append(relative)
                continue
            ensure_dir(target.parent)
            shutil.copy2(backup_path, target)
            restored.append(relative)
        else:
            if target.exists():
                if target.is_file():
                    target.unlink()
                elif target.is_dir():
                    shutil.rmtree(target)
            removed.append(relative)
    return {
        'restored_files': restored,
        'removed_files': removed,
        'missing_backups': missing_backups,
    }


def render_manifest_md(manifest: dict[str, Any]) -> str:
    lines = [
        f"# {manifest.get('phase_name')} | {manifest.get('mode')}",
        '',
        f"- run_id: `{manifest.get('run_id')}`",
        f"- transaction_id: `{manifest.get('transaction_id')}`",
        f"- checkpoint_label: `{manifest.get('checkpoint_label')}`",
        f"- requested_by: `{manifest.get('requested_by')}`",
        f"- root_dir: `{manifest.get('root_dir')}`",
        f"- export_dir: `{manifest.get('export_dir')}`",
        '',
        '## Touched files',
        '',
    ]
    for row in list(manifest.get('touched_files') or []):
        lines.append(f"- `{row}`")
    lines.extend(['', '## Notes', ''])
    for row in list(manifest.get('notes') or []):
        lines.append(f'- {row}')
    lines.append('')
    return '\n'.join(lines)


def run_subprocess_logged(cmd: list[str], *, cwd: Path, log_path: Path) -> dict[str, Any]:
    ensure_dir(log_path.parent)
    completed = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding='utf-8', errors='replace')
    content = []
    content.append(f'$ {" ".join(cmd)}')
    content.append('')
    content.append(completed.stdout or '')
    if completed.stderr:
        content.append('\n[stderr]\n')
        content.append(completed.stderr)
    write_text(log_path, '\n'.join(content).strip() + '\n')
    return {
        'command': cmd,
        'returncode': int(completed.returncode),
        'log_path': str(log_path),
    }


def default_test_command(*, root_dir: Path, tests: list[str]) -> list[str]:
    return [sys.executable, '-m', 'pytest', *tests]


def write_rollback_instructions(path: Path, *, transaction_file: Path, script_path: Path, root_dir: Path) -> None:
    lines = [
        'Rollback instructions',
        '',
        f'1. Transaction file: {transaction_file}',
        f'2. Root dir: {root_dir}',
        '',
        'Command:',
        f'py "{script_path}" --root-dir "{root_dir}" --mode rollback --transaction-file "{transaction_file}"',
        '',
    ]
    write_text(path, '\n'.join(lines))


def build_config_from_args(args: argparse.Namespace, *, phase_name: str) -> PhaseConfig:
    root_dir = resolve_root_dir(args.root_dir)
    export_dir = resolve_export_dir(getattr(args, 'export_dir', ''), root_dir=root_dir)
    checkpoint_label = safe_slug(getattr(args, 'checkpoint_label', ''), fallback=f'{phase_name}-{args.mode}')
    transaction_file = Path(str(args.transaction_file)).expanduser().resolve() if str(getattr(args, 'transaction_file', '')).strip() else None
    return PhaseConfig(
        phase_name=phase_name,
        root_dir=root_dir,
        export_dir=export_dir,
        mode=str(args.mode),
        run_tests=bool(getattr(args, 'run_tests', False)),
        checkpoint_label=checkpoint_label,
        requested_by=str(getattr(args, 'requested_by', DEFAULT_REQUESTED_BY) or DEFAULT_REQUESTED_BY),
        allow_dirty_worktree=bool(getattr(args, 'allow_dirty_worktree', False)),
        skip_smoke=bool(getattr(args, 'skip_smoke', False)),
        json_output=bool(getattr(args, 'json', False)),
        transaction_file=transaction_file,
    )


def emit_json_summary(payload: dict[str, Any], *, enabled: bool) -> None:
    if enabled:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
