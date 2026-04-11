#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Small git snapshot helpers for policy/intervention layers."""

import subprocess
from pathlib import Path
from typing import Any


def _run_git(repo_root: Path, *args: str) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            ['git', '-C', str(repo_root), *args],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception as exc:
        return False, f'{type(exc).__name__}: {exc}'
    output = (completed.stdout or '').strip() or (completed.stderr or '').strip()
    return completed.returncode == 0, output



def discover_repo_root(start_path: Path) -> Path | None:
    current = Path(start_path).resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / '.git').exists():
            return candidate
    ok, output = _run_git(current, 'rev-parse', '--show-toplevel')
    if ok and output:
        return Path(output).resolve()
    return None



def collect_git_snapshot(start_path: Path) -> dict[str, Any]:
    repo_root = discover_repo_root(Path(start_path))
    if repo_root is None:
        return {
            'summary': {
                'is_repo': False,
                'repo_root': None,
                'worktree': str(Path(start_path).resolve()),
                'dirty_file_count': 0,
                'branch': None,
                'head': None,
                'status_lines': [],
            }
        }
    ok_status, status_output = _run_git(repo_root, 'status', '--porcelain')
    ok_branch, branch_output = _run_git(repo_root, 'rev-parse', '--abbrev-ref', 'HEAD')
    ok_head, head_output = _run_git(repo_root, 'rev-parse', 'HEAD')
    status_lines = [line for line in status_output.splitlines() if line.strip()] if ok_status else []
    return {
        'summary': {
            'is_repo': True,
            'repo_root': str(repo_root),
            'worktree': str(repo_root),
            'dirty_file_count': len(status_lines),
            'branch': branch_output if ok_branch else None,
            'head': head_output if ok_head else None,
            'status_lines': status_lines[:200],
        }
    }
