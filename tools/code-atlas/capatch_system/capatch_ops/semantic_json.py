from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base import fail


def _decode_segment(segment: str) -> str:
    return segment.replace("~1", "/").replace("~0", "~")


def _pointer_parts(pointer: str) -> list[str]:
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        fail(f"json_pointer invalido: {pointer}")
    return [_decode_segment(part) for part in pointer.split("/")[1:]]


def _resolve_parent(document: Any, pointer: str, create: bool = False) -> tuple[Any, str | None]:
    parts = _pointer_parts(pointer)
    if not parts:
        return None, None
    current = document
    for part in parts[:-1]:
        if isinstance(current, dict):
            if part not in current:
                if not create:
                    fail(f"json_pointer no encontrado: {pointer}")
                current[part] = {}
            current = current[part]
        else:
            fail(f"json_pointer invalido: {pointer}")
    return current, parts[-1]


def _serialize(document: Any) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def render_set_json_value(target: Path, content: str, json_pointer: str, value: Any, label: str) -> str:
    document = json.loads(content)
    parent, key = _resolve_parent(document, json_pointer, create=True)
    if parent is None:
        document = value
    elif isinstance(parent, dict):
        parent[key] = value
    else:
        fail(f"json_pointer invalido para {label} en {target}: {json_pointer}")
    return _serialize(document)


def render_delete_json_key(target: Path, content: str, json_pointer: str, label: str) -> str:
    document = json.loads(content)
    parent, key = _resolve_parent(document, json_pointer, create=False)
    if parent is None:
        fail(f"No se puede borrar el documento raiz para {label} en {target}")
    if isinstance(parent, dict) and key in parent:
        del parent[key]
    else:
        fail(f"json_pointer no encontrado para {label} en {target}: {json_pointer}")
    return _serialize(document)


def render_merge_json_object(target: Path, content: str, json_pointer: str, object_value: Any, label: str) -> str:
    if not isinstance(object_value, dict):
        fail(f"object_value debe ser objeto para {label} en {target}")
    document = json.loads(content)
    if json_pointer == "":
        if not isinstance(document, dict):
            fail(f"El documento raiz no es un objeto para {label} en {target}")
        document.update(object_value)
        return _serialize(document)
    parent, key = _resolve_parent(document, json_pointer, create=True)
    if not isinstance(parent, dict):
        fail(f"json_pointer invalido para {label} en {target}: {json_pointer}")
    current = parent.get(key)
    if current is None:
        parent[key] = dict(object_value)
    elif isinstance(current, dict):
        current.update(object_value)
    else:
        fail(f"json_pointer para {label} en {target} no apunta a un objeto")
    return _serialize(document)
