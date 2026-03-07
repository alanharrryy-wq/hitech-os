from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class DiffSelection:
    enabled: bool
    git_available: bool
    root: Path
    base_ref: str
    changed_files: frozenset[str] = field(default_factory=frozenset)
    untracked_files: frozenset[str] = field(default_factory=frozenset)
    mode: str = 'all'
    error: str | None = None

    def allows(self, relpath: str) -> bool:
        if not self.enabled or not self.git_available:
            return True
        if not self.changed_files and not self.untracked_files:
            return True
        return relpath in self.changed_files or relpath in self.untracked_files


class GitDiffScanner:
    def __init__(self, repo_root: str | Path) -> None:
        self.repo_root = Path(repo_root).resolve()

    def build_selection(
        self,
        *,
        enabled: bool,
        base_ref: str,
        include_untracked: bool = True,
        staged_only: bool = False,
    ) -> DiffSelection:
        if not enabled:
            return DiffSelection(enabled=False, git_available=False, root=self.repo_root, base_ref=base_ref)
        if not self._is_git_repo():
            return DiffSelection(
                enabled=True,
                git_available=False,
                root=self.repo_root,
                base_ref=base_ref,
                error='git repository not detected',
            )
        try:
            changed = self._read_changed(base_ref=base_ref, staged_only=staged_only)
            untracked = self._read_untracked() if include_untracked else frozenset()
            return DiffSelection(
                enabled=True,
                git_available=True,
                root=self.repo_root,
                base_ref=base_ref,
                changed_files=changed,
                untracked_files=untracked,
                mode='staged' if staged_only else 'working-tree',
            )
        except Exception as exc:
            return DiffSelection(
                enabled=True,
                git_available=False,
                root=self.repo_root,
                base_ref=base_ref,
                error=str(exc),
            )

    def _run(self, *args: str) -> str:
        completed = subprocess.run(
            ['git', '-C', str(self.repo_root), *args],
            capture_output=True,
            check=True,
            encoding='utf-8',
            errors='replace',
        )
        return completed.stdout

    def _is_git_repo(self) -> bool:
        try:
            self._run('rev-parse', '--show-toplevel')
            return True
        except Exception:
            return False

    def _read_changed(self, *, base_ref: str, staged_only: bool) -> frozenset[str]:
        if staged_only:
            stdout = self._run('diff', '--cached', '--name-only', '--diff-filter=ACMR')
        else:
            stdout = self._run('diff', '--name-only', '--diff-filter=ACMR', base_ref)
        return frozenset(self._normalize_lines(stdout))

    def _read_untracked(self) -> frozenset[str]:
        stdout = self._run('ls-files', '--others', '--exclude-standard')
        return frozenset(self._normalize_lines(stdout))

    @staticmethod
    def _normalize_lines(stdout: str) -> list[str]:
        values: list[str] = []
        for raw in stdout.splitlines():
            clean = raw.strip().replace('\\', '/')
            if clean:
                values.append(clean)
        return values
