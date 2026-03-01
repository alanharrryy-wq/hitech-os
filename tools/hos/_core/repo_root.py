#!/usr/bin/env python3
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_ROOT_MARKERS: tuple[str, ...] = (
    "package.json",
    "pnpm-workspace.yaml",
    "turbo.json",
)


@dataclass(frozen=True)
class RootProbeResult:
    root: Path
    matched_markers: tuple[str, ...]


def _candidate_starts(start: Path | None = None) -> list[Path]:
    points: list[Path] = []

    env_root = os.getenv("HOS_REPO_ROOT")
    if env_root:
        points.append(Path(env_root).resolve())

    if start is not None:
        points.append(start.resolve())
    else:
        points.append(Path.cwd().resolve())

    unique: list[Path] = []
    seen: set[str] = set()
    for point in points:
        key = point.as_posix().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(point)

    return unique


def _iter_ancestors(path: Path) -> Iterable[Path]:
    current = path
    if current.is_file():
        current = current.parent
    while True:
        yield current
        if current.parent == current:
            break
        current = current.parent


def probe_repo_root(
    start: Path | None = None,
    markers: tuple[str, ...] = DEFAULT_ROOT_MARKERS,
) -> RootProbeResult | None:
    if not markers:
        raise ValueError("markers must not be empty")

    for start_point in _candidate_starts(start):
        for candidate in _iter_ancestors(start_point):
            matched = tuple(marker for marker in markers if (candidate / marker).exists())
            if len(matched) == len(markers):
                return RootProbeResult(root=candidate, matched_markers=matched)
    return None


def find_repo_root(
    start: Path | None = None,
    markers: tuple[str, ...] = DEFAULT_ROOT_MARKERS,
) -> Path:
    probed = probe_repo_root(start=start, markers=markers)
    if probed is None:
        marker_line = ", ".join(markers)
        raise FileNotFoundError(f"unable to detect repository root, required markers: {marker_line}")
    return probed.root


def is_repo_root(path: Path, markers: tuple[str, ...] = DEFAULT_ROOT_MARKERS) -> bool:
    candidate = path.resolve()
    return all((candidate / marker).exists() for marker in markers)


def relative_to_root(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()

