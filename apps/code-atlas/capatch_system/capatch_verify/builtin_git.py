#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import subprocess
from pathlib import Path

from .base import VerifierResultRow


def run_git_clean(target_files: list[str], ctx: dict[str, object]) -> list[dict[str, object]]:
    root_dir = Path(str((ctx or {}).get('root_dir') or '.')).resolve()
    try:
        completed = subprocess.run(['git', '-C', str(root_dir), 'status', '--porcelain'], capture_output=True, text=True, timeout=20, check=False)
        ok = completed.returncode == 0
        output = (completed.stdout or '').strip() or (completed.stderr or '').strip()
        detail = 'working tree clean' if ok and not output else output[:2000]
        if ok and not output:
            return [VerifierResultRow('git-clean', True, 'Git working tree clean', detail, metrics={'root_dir': str(root_dir)}).to_dict()]
        return [VerifierResultRow('git-clean', ok, 'Git status captured', detail, metrics={'root_dir': str(root_dir)}).to_dict()]
    except Exception as exc:
        return [VerifierResultRow('git-clean', False, 'Git status failed', f'{type(exc).__name__}: {exc}', metrics={'root_dir': str(root_dir)}).to_dict()]
