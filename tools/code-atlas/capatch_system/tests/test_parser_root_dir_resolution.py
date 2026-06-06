from __future__ import annotations

from pathlib import Path

from capatch_cli.parser import resolve_root_dir
from capatch_contracts.constants import DEFAULT_ROOT_DIR


def test_default_root_dir_falls_back_to_repo_root_when_cwd_variant_is_missing(tmp_path: Path) -> None:
    cwd = tmp_path / 'cwd'
    cwd.mkdir(parents=True, exist_ok=True)
    repo_root = tmp_path / 'repo'
    repo_root.mkdir(parents=True, exist_ok=True)
    expected = (repo_root / DEFAULT_ROOT_DIR).resolve()
    expected.mkdir(parents=True, exist_ok=True)

    resolved = resolve_root_dir(str(DEFAULT_ROOT_DIR), cwd=cwd, repo_root=repo_root)
    assert resolved == expected


def test_explicit_relative_root_dir_stays_cwd_relative(tmp_path: Path) -> None:
    cwd = tmp_path / 'cwd'
    cwd.mkdir(parents=True, exist_ok=True)
    repo_root = tmp_path / 'repo'
    repo_root.mkdir(parents=True, exist_ok=True)

    resolved = resolve_root_dir('custom-root', cwd=cwd, repo_root=repo_root)
    assert resolved == (cwd / 'custom-root').resolve()


def test_absolute_root_dir_is_returned_as_is(tmp_path: Path) -> None:
    absolute = (tmp_path / 'absolute-root').resolve()
    resolved = resolve_root_dir(str(absolute), cwd=tmp_path, repo_root=tmp_path / 'repo')
    assert resolved == absolute
