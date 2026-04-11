#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Helpers de filesystem para runtime diagnostico y plugins."""

import os
import tempfile
from pathlib import Path
from typing import Any


def ensure_dir(path_value: Path) -> Path:
    path_value = Path(path_value)
    path_value.mkdir(parents=True, exist_ok=True)
    return path_value


def read_text_safe(path_value: Path, default: str = "") -> str:
    path_value = Path(path_value)
    try:
        return path_value.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return default


def atomic_write_text(path_value: Path, text: str) -> None:
    path_value = Path(path_value)
    ensure_dir(path_value.parent)
    fd, tmp_name = tempfile.mkstemp(prefix=path_value.name + ".", suffix=".tmp", dir=str(path_value.parent))
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        tmp_path.write_text(str(text), encoding="utf-8", newline="")
        tmp_path.replace(path_value)
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass


def safe_file_size(path_value: Path) -> int | None:
    path_value = Path(path_value)
    try:
        return path_value.stat().st_size
    except Exception:
        return None


def list_files_limited(root_dir: Path, limit: int = 40) -> list[dict[str, Any]]:
    root_dir = Path(root_dir)
    items: list[dict[str, Any]] = []
    if not root_dir.exists():
        return items
    try:
        iterable = sorted(root_dir.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
    except Exception:
        return items
    for item in iterable[:limit]:
        try:
            items.append(
                {
                    "name": item.name,
                    "path": str(item.resolve()),
                    "is_dir": item.is_dir(),
                    "size": None if item.is_dir() else item.stat().st_size,
                }
            )
        except Exception:
            items.append({"name": item.name, "path": str(item), "is_dir": False, "size": None})
    return items
