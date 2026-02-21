from __future__ import annotations

import difflib
import subprocess
from typing import Iterable

from .common import REPO_ROOT


def _git_show(path: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"HEAD:{path}"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout or ""


def unified_patch_for_paths(paths: Iterable[str]) -> str:
    chunks: list[str] = []
    for rel_path in sorted({path for path in paths if path}):
        new_path = REPO_ROOT / rel_path
        new_text = new_path.read_text(encoding="utf-8") if new_path.exists() else ""
        old_text = _git_show(rel_path)

        old_lines = old_text.splitlines(keepends=False)
        new_lines = new_text.splitlines(keepends=False)
        patch = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{rel_path}",
            tofile=f"b/{rel_path}",
            lineterm="",
        )
        rendered = "\n".join(patch)
        if rendered.strip():
            chunks.append(rendered + "\n")
    return "\n".join(chunks).rstrip() + ("\n" if chunks else "")
