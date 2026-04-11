from __future__ import annotations

import subprocess
from pathlib import Path


def _run_git(root_dir: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(root_dir),
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def capture_git_state(root_dir: Path) -> dict[str, object]:
    return {
        "git_branch": _run_git(root_dir, "rev-parse", "--abbrev-ref", "HEAD"),
        "git_head": _run_git(root_dir, "rev-parse", "HEAD"),
        "git_dirty": bool(_run_git(root_dir, "status", "--porcelain")),
    }
