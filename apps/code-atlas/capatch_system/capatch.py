#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Compatibility launcher for capatch CLI.

Real runtime ownership lives in capatch_cli.main. This module only wraps that
entrypoint with workspace-cleaner hooks and a compatibility notice.
"""

import os
import sys
from pathlib import Path

from capatch_cli.main import main as _cli_main
from capatch_runtime.workspace_cleaner import (
    load_workspace_cleaner_policy,
    run_shutdown_cleaner,
    run_startup_cleaner,
)


def _bool_env(name: str) -> bool:
    return os.environ.get(name, '').strip().lower() in {'1', 'true', 'yes', 'on'}


def _safe_stderr(message: str) -> None:
    try:
        print(message, file=sys.stderr)
    except Exception:
        pass


def _safe_startup_cleaner(base_dir: Path, *, policy: dict[str, object], dry_run: bool) -> dict[str, object]:
    try:
        return dict(run_startup_cleaner(base_dir, policy=policy, dry_run=dry_run) or {})
    except Exception as exc:
        _safe_stderr(f'[WARN] startup cleaner degraded: {type(exc).__name__}: {exc}')
        return {'status': 'degraded', 'error': f'{type(exc).__name__}: {exc}'}


def _safe_shutdown_cleaner(base_dir: Path, *, policy: dict[str, object], dry_run: bool, run_summary: dict[str, object]) -> None:
    try:
        run_shutdown_cleaner(base_dir, policy=policy, dry_run=dry_run, run_summary=run_summary)
    except Exception as exc:
        _safe_stderr(f'[WARN] shutdown cleaner degraded: {type(exc).__name__}: {exc}')


def _emit_compat_notice() -> None:
    _safe_stderr('[WARN] capatch.py opera como shim de compatibilidad. El entrypoint real ya es capatch_cli.main.')


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    _emit_compat_notice()

    base_dir = Path(__file__).resolve().parent
    if _bool_env('CAPATCH_SKIP_CLEANER'):
        return int(_cli_main(argv))

    policy = load_workspace_cleaner_policy(base_dir)
    dry_run = '--dry-run' in argv
    startup_report = _safe_startup_cleaner(base_dir, policy=policy, dry_run=dry_run)
    run_summary: dict[str, object] = {
        'argv': argv,
        'startup_status': startup_report.get('status'),
    }
    returncode: int | None = None
    try:
        returncode = int(_cli_main(argv))
        return returncode
    finally:
        run_summary['returncode'] = returncode
        _safe_shutdown_cleaner(base_dir, policy=policy, dry_run=dry_run, run_summary=run_summary)


if __name__ == '__main__':
    raise SystemExit(main())

