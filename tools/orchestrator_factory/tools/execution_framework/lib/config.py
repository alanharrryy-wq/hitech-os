
from __future__ import annotations

from pathlib import Path
from .common import discover_repo_root, read_json


def load_system_config(repo_root: Path | None = None) -> dict:
    root = repo_root or discover_repo_root(Path(__file__).resolve())
    return read_json(root / 'configs/execution_framework/system_config.json')


def load_path_policies(repo_root: Path | None = None) -> dict:
    root = repo_root or discover_repo_root(Path(__file__).resolve())
    return read_json(root / 'configs/execution_framework/path_policies.json')


def load_target_layout(repo_root: Path | None = None) -> dict:
    root = repo_root or discover_repo_root(Path(__file__).resolve())
    return read_json(root / 'configs/execution_framework/repo_target_layout.json')


def load_parallel_manifest(repo_root: Path | None = None) -> dict:
    root = repo_root or discover_repo_root(Path(__file__).resolve())
    return read_json(root / 'parallel_manifest.json')


def load_tree_hygiene_config(repo_root: Path | None = None) -> dict:
    root = repo_root or discover_repo_root(Path(__file__).resolve())
    system = load_system_config(root)
    return read_json(root / system['tree_hygiene_config'])
