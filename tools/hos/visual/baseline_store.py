#!/usr/bin/env python3
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from tools.hos._core.hashing import sha256_file


@dataclass(frozen=True)
class BaselinePaths:
    base_dir: Path
    current_dir: Path
    diff_dir: Path


def resolve_baseline_paths(repo_root: Path, suite: str) -> BaselinePaths:
    safe_suite = suite.replace("\\", "_").replace("/", "_").strip("_") or "default"
    base_dir = (repo_root / "docs/visual-baselines" / safe_suite).resolve()
    current_dir = (repo_root / "tools/_local/visual/current" / safe_suite).resolve()
    diff_dir = (repo_root / "tools/_local/visual/diff" / safe_suite).resolve()
    base_dir.mkdir(parents=True, exist_ok=True)
    current_dir.mkdir(parents=True, exist_ok=True)
    diff_dir.mkdir(parents=True, exist_ok=True)
    return BaselinePaths(base_dir=base_dir, current_dir=current_dir, diff_dir=diff_dir)


def list_png_files(root: Path) -> list[Path]:
    files = [path for path in root.rglob("*.png") if path.is_file()]
    files.sort(key=lambda item: item.relative_to(root).as_posix())
    return files


def sync_captures_to_current(capture_root: Path, current_root: Path) -> list[Path]:
    copied: list[Path] = []
    for source in list_png_files(capture_root):
        rel = source.relative_to(capture_root)
        target = current_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(target)
    return copied


def update_baselines(current_root: Path, baseline_root: Path) -> list[Path]:
    updated: list[Path] = []
    for source in list_png_files(current_root):
        rel = source.relative_to(current_root)
        target = baseline_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        updated.append(target)
    return updated


def compare_file_hashes(left: Path, right: Path) -> bool:
    if not left.exists() or not right.exists():
        return False
    if left.stat().st_size != right.stat().st_size:
        return False
    return sha256_file(left) == sha256_file(right)

