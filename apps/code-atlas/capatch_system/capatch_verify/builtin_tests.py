#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

from .base import VerifierResultRow


def run_tests(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    root_dir = Path(str((ctx or {}).get('root_dir') or '.')).resolve()
    command = (ctx or {}).get('test_command')
    if not command:
        return [VerifierResultRow('tests', True, 'Test verifier skipped', 'No test_command configured in ctx.', metrics={'root_dir': str(root_dir)}).to_dict()]
    argv = command if isinstance(command, list) else shlex.split(str(command))
    try:
        completed = subprocess.run(argv, cwd=str(root_dir), capture_output=True, text=True, timeout=120, check=False)
        output = ((completed.stdout or '') + '\n' + (completed.stderr or '')).strip()[:4000]
        return [VerifierResultRow('tests', completed.returncode == 0, 'Test verifier executed', output or 'sin salida', metrics={'root_dir': str(root_dir), 'command': argv}).to_dict()]
    except Exception as exc:
        return [VerifierResultRow('tests', False, 'Test verifier failed', f'{type(exc).__name__}: {exc}', metrics={'root_dir': str(root_dir), 'command': argv}).to_dict()]
