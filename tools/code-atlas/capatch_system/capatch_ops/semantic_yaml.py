from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .base import fail


def _path_parts(path_value: str) -> list[str]:
    parts = [part for part in str(path_value).split(".") if part]
    if not parts:
        fail(f"yaml_path invalido: {path_value}")
    return parts


def _load_yaml(content: str) -> Any:
    return yaml.safe_load(content) if content.strip() else {}


def _dump_yaml(payload: Any) -> str:
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def render_set_yaml_value(target: Path, content: str, yaml_path: str, value: Any, label: str) -> str:
    document = _load_yaml(content)
    if document is None:
        document = {}
    current = document
    parts = _path_parts(yaml_path)
    for part in parts[:-1]:
        if not isinstance(current, dict):
            fail(f"yaml_path invalido para {label} en {target}: {yaml_path}")
        current = current.setdefault(part, {})
    if not isinstance(current, dict):
        fail(f"yaml_path invalido para {label} en {target}: {yaml_path}")
    current[parts[-1]] = value
    return _dump_yaml(document)


def render_delete_yaml_key(target: Path, content: str, yaml_path: str, label: str) -> str:
    document = _load_yaml(content)
    current = document
    parts = _path_parts(yaml_path)
    for part in parts[:-1]:
        if not isinstance(current, dict) or part not in current:
            fail(f"yaml_path no encontrado para {label} en {target}: {yaml_path}")
        current = current[part]
    if not isinstance(current, dict) or parts[-1] not in current:
        fail(f"yaml_path no encontrado para {label} en {target}: {yaml_path}")
    del current[parts[-1]]
    return _dump_yaml(document)
