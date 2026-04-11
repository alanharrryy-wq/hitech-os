from __future__ import annotations

from pathlib import Path
from typing import Any

import tomlkit

from .base import fail


def _path_parts(path_value: str) -> list[str]:
    parts = [part for part in str(path_value).split(".") if part]
    if not parts:
        fail(f"toml_path invalido: {path_value}")
    return parts


def render_set_toml_value(target: Path, content: str, toml_path: str, value: Any, label: str) -> str:
    document = tomlkit.parse(content) if content.strip() else tomlkit.document()
    current = document
    parts = _path_parts(toml_path)
    for part in parts[:-1]:
        if part not in current or not hasattr(current[part], "items"):
            current[part] = tomlkit.table()
        current = current[part]
    current[parts[-1]] = value
    return tomlkit.dumps(document)
