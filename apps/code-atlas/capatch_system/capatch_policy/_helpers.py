#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable


def get_attr_or_key(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def normalize_target_files(preflight: Any | None, operations: Iterable[Any] | None) -> list[str]:
    target_files: list[str] = []
    if preflight is not None:
        raw = get_attr_or_key(preflight, 'target_files', []) or []
        target_files.extend(str(item) for item in raw if str(item))
    for operation in list(operations or []):
        candidate = get_attr_or_key(operation, 'file')
        if not candidate:
            spec = get_attr_or_key(operation, 'spec')
            candidate = get_attr_or_key(spec, 'file') if spec is not None else None
        if candidate:
            target_files.append(str(candidate))
    seen = set()
    ordered: list[str] = []
    for item in target_files:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def path_suffixes(path_value: str) -> tuple[str, str]:
    path = Path(path_value)
    suffix = path.suffix.lower()
    return path.name.lower(), suffix
