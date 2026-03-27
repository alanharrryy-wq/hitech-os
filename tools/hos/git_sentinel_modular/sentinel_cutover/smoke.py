from __future__ import annotations

import ast
from pathlib import Path

def _check_dir_exists(path: str | Path) -> bool:
    return Path(path).exists()

def _python_parse_check(path: str | Path) -> bool:
    file_path = Path(path)
    ast.parse(file_path.read_text(encoding="utf-8"))
    return True

def run_smoke_checks(workspace_root: str | Path) -> dict:
    workspace = Path(workspace_root)
    candidate = workspace / "candidate"
    py_files = list(candidate.rglob("*.py"))
    parsed = 0
    for file_path in py_files[:20]:
        _python_parse_check(file_path)
        parsed += 1
    return {
        "candidate_present": _check_dir_exists(candidate),
        "parsed_python_files": parsed,
        "status": "ready",
    }
