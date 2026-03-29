from __future__ import annotations

import ast
from pathlib import Path

def _python_parse_check(path: str | Path) -> bool:
    file_path = Path(path)
    ast.parse(file_path.read_text(encoding="utf-8"))
    return True

def run_post_execution_smoke(target_root: str | Path) -> dict:
    root = Path(target_root)
    parsed = 0
    for file_path in list(root.rglob("*.py"))[:20]:
        _python_parse_check(file_path)
        parsed += 1
    return {"status": "ok", "parsed_python_files": parsed}
