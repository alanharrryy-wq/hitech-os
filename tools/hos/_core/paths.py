#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .stable_json import load_json

DEFAULT_FORBIDDEN_PATHS: tuple[str, ...] = (
    ".git",
    "node_modules",
    "tools/_local",
    "docs/_root_archive",
    "tools/codex/worktrees",
    ".turbo",
)


@dataclass(frozen=True)
class ForbiddenRegistry:
    entries: tuple[str, ...]

    def is_forbidden(self, relative_path: str) -> bool:
        normalized = relative_path.replace("\\", "/").strip("/")
        for entry in self.entries:
            if not entry:
                continue
            if normalized == entry:
                return True
            if normalized.startswith(entry + "/"):
                return True
        return False


def is_within(base: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def assert_within(base: Path, target: Path) -> Path:
    resolved = target.resolve()
    if not is_within(base, resolved):
        raise ValueError(f"path escapes base directory: {resolved} not inside {base.resolve()}")
    return resolved


def safe_join(base: Path, *parts: str) -> Path:
    if not parts:
        return base.resolve()
    candidate = base
    for part in parts:
        if part is None:
            raise ValueError("path segment must not be None")
        normalized = part.replace("\\", "/")
        if normalized.startswith("../") or normalized == "..":
            raise ValueError(f"path traversal not allowed: {part}")
        candidate = candidate / normalized
    return assert_within(base, candidate)


def load_forbidden_registry(config_path: Path | None = None) -> ForbiddenRegistry:
    if config_path is None or not config_path.exists():
        return ForbiddenRegistry(entries=DEFAULT_FORBIDDEN_PATHS)

    payload = load_json(config_path)
    if not isinstance(payload, dict):
        raise ValueError(f"forbidden registry must be object: {config_path}")

    values = payload.get("forbidden", [])
    if not isinstance(values, list):
        raise ValueError("forbidden registry key 'forbidden' must be list")

    entries = sorted(
        {
            item.replace("\\", "/").strip("/")
            for item in values
            if isinstance(item, str) and item.strip()
        }
    )
    if not entries:
        entries = list(DEFAULT_FORBIDDEN_PATHS)
    return ForbiddenRegistry(entries=tuple(entries))


def collect_forbidden_hits(
    root: Path,
    paths: Iterable[Path],
    registry: ForbiddenRegistry,
) -> list[str]:
    hits: list[str] = []
    for path in paths:
        try:
            rel = path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
        if registry.is_forbidden(rel):
            hits.append(rel)
    return sorted(set(hits))

