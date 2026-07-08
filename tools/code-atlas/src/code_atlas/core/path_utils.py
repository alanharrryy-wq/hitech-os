"""Neutral path utilities for Code Atlas.

Do not hardcode local machines or project-specific roots in Code Atlas core.
Use a loaded ProjectProfile and relative paths instead.
"""
from __future__ import annotations
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def as_path(value: PathLike) -> Path:
    return value if isinstance(value, Path) else Path(str(value))


def to_posix_relative(path: PathLike, root: PathLike) -> str:
    path_p = as_path(path).resolve()
    root_p = as_path(root).resolve()
    try:
        return path_p.relative_to(root_p).as_posix()
    except ValueError:
        return path_p.as_posix()


def display_path(path: PathLike, root: PathLike, root_token: str = "<PROJECT_ROOT>") -> str:
    rel = to_posix_relative(path, root)
    if rel.startswith("..") or rel.startswith(":"):
        return as_path(path).as_posix()
    return f"{root_token}/{rel}" if rel else root_token
