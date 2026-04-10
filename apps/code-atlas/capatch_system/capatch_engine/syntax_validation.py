from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

import yaml


def build_syntax_validation_plan(target_files: list[str]) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    for file_name in target_files:
        suffix = Path(file_name).suffix.lower()
        if suffix == ".py":
            verifier = "python-parse"
        elif suffix == ".json":
            verifier = "json-parse"
        elif suffix in {".yaml", ".yml"}:
            verifier = "yaml-parse"
        elif suffix == ".toml":
            verifier = "toml-parse"
        elif suffix in {".ts", ".tsx", ".js", ".jsx"}:
            verifier = "typescript-parse"
        else:
            verifier = "none"
        plan.append({"target_file": file_name, "verifier": verifier})
    return plan


def validate_content_by_path(path_value: Path, content: str) -> list[dict[str, Any]]:
    suffix = path_value.suffix.lower()
    issues: list[dict[str, Any]] = []
    try:
        if suffix == ".py":
            compile(content, str(path_value), "exec")
        elif suffix == ".json":
            json.loads(content)
        elif suffix in {".yaml", ".yml"}:
            yaml.safe_load(content) if content.strip() else None
        elif suffix == ".toml":
            tomllib.loads(content)
    except Exception as exc:
        issues.append({"target_file": path_value.as_posix(), "error": str(exc)})
    return issues
