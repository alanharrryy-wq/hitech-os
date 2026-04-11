#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Compat minima de PyYAML para CAPATCH.

Objetivo:
- permitir `import yaml` sin dependencia externa
- soportar safe_load/safe_dump para casos simples usados por smoke y plugin health

No intenta cubrir YAML completo.
"""

import json
from typing import Any, Iterator


__all__ = [
    "safe_load",
    "safe_dump",
    "safe_load_all",
    "load",
    "dump",
]


def safe_load(content: str) -> Any:
    source = str(content or "")
    if not source.strip():
        return None
    try:
        return json.loads(source)
    except Exception:
        return _parse_simple_yaml_mapping(source)


def safe_load_all(content: str) -> Iterator[Any]:
    value = safe_load(content)
    if value is None:
        return iter(())
    return iter((value,))


def safe_dump(payload: Any, sort_keys: bool = False, allow_unicode: bool = True, **_: Any) -> str:
    if isinstance(payload, dict):
        lines: list[str] = []
        _emit_simple_yaml(lines, payload, indent=0, sort_keys=sort_keys)
        rendered = "\n".join(lines).rstrip()
        return rendered + ("\n" if rendered else "")
    return json.dumps(payload, ensure_ascii=not allow_unicode, indent=2) + "\n"


def load(content: str, *args: Any, **kwargs: Any) -> Any:
    return safe_load(content)


def dump(payload: Any, *args: Any, **kwargs: Any) -> str:
    return safe_dump(payload, *args, **kwargs)


def _parse_simple_yaml_mapping(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if "\t" in raw_line[:indent]:
            raise ValueError(f"YAML con tabs no soportado (linea {line_number}).")

        line = raw_line.strip()
        if ":" not in line:
            raise ValueError(f"YAML no soportado en linea {line_number}: {line}")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value_text = raw_value.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ValueError(f"Indentacion YAML invalida en linea {line_number}.")

        parent = stack[-1][1]
        if value_text == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(value_text)

    return root


def _parse_scalar(raw_value: str) -> Any:
    value = raw_value.strip()
    if value == "":
        return ""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "none", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        return int(value)
    except Exception:
        pass
    try:
        return float(value)
    except Exception:
        pass
    return value


def _emit_simple_yaml(lines: list[str], payload: dict[str, Any], *, indent: int, sort_keys: bool) -> None:
    keys = sorted(payload.keys()) if sort_keys else list(payload.keys())
    prefix = " " * indent
    for key in keys:
        value = payload[key]
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            _emit_simple_yaml(lines, value, indent=indent + 2, sort_keys=sort_keys)
        else:
            lines.append(f"{prefix}{key}: {_format_scalar(value)}")


def _format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)

    text = str(value)
    if text == "" or any(ch.isspace() for ch in text) or ":" in text or "#" in text:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text