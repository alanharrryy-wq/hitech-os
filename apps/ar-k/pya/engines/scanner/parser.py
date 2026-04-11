from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


def classify_file(relative_path: str) -> str:
    if relative_path.endswith(".py"):
        return "python"
    if relative_path.endswith(".json"):
        return "json"
    if relative_path.endswith(".md"):
        return "markdown"
    return "other"


def parse_python_file(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {
            "ok": False,
            "imports": [],
            "exports": [],
            "error": {
                "message": exc.msg,
                "lineno": exc.lineno,
                "offset": exc.offset,
            },
        }

    imports: list[str] = []
    exports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level + (node.module or "")
            imports.append(prefix)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and getattr(node, "col_offset", 1) == 0:
            exports.append(node.name)
        elif isinstance(node, ast.Assign) and getattr(node, "col_offset", 1) == 0:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    try:
                        value = ast.literal_eval(node.value)
                    except Exception:
                        continue
                    if isinstance(value, (list, tuple)):
                        exports.extend(str(item) for item in value)

    return {
        "ok": True,
        "imports": sorted(set(imports)),
        "exports": sorted(set(exports)),
        "error": None,
    }
