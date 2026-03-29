from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from ..shared.contracts import ScanResult, ScanStats
from ..shared.errors import ConfigurationError
from ..shared.foundation import ensure_inside_root


DEFAULT_IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    ".next",
    ".cache",
    ".pytest_cache",
    "dist",
    "build",
}
DEFAULT_IGNORED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".tmp",
    ".bak",
}


@dataclass(slots=True)
class ScanRequest:
    repo_root: Path
    ignored_directories: set[str] = field(default_factory=lambda: set(DEFAULT_IGNORED_DIRECTORIES))
    ignored_suffixes: set[str] = field(default_factory=lambda: set(DEFAULT_IGNORED_SUFFIXES))
    include_hidden: bool = False
    max_files: int = 20000

    def validate(self) -> "ScanRequest":
        self.repo_root = Path(self.repo_root).resolve()
        if not self.repo_root.exists():
            raise ConfigurationError("ScanRequest repo_root does not exist.", repo_root=str(self.repo_root))
        if not self.repo_root.is_dir():
            raise ConfigurationError("ScanRequest repo_root must be a directory.", repo_root=str(self.repo_root))
        if not isinstance(self.max_files, int) or self.max_files <= 0:
            raise ConfigurationError("max_files must be a positive integer.", max_files=self.max_files)
        return self


@dataclass(slots=True)
class RepositorySnapshot:
    repo_root: str
    discovered_files: list[str]
    discovered_directories: list[str]
    truncated: bool = False

    def to_stats(self) -> ScanStats:
        return ScanStats(
            scanned_files=len(self.discovered_files),
            scanned_directories=len(self.discovered_directories),
        ).validate()


class RepositoryScanner:
    def __init__(self, ignored_directories: Iterable[str] | None = None, ignored_suffixes: Iterable[str] | None = None):
        self.ignored_directories = set(ignored_directories or DEFAULT_IGNORED_DIRECTORIES)
        self.ignored_suffixes = set(ignored_suffixes or DEFAULT_IGNORED_SUFFIXES)

    def build_request(self, repo_root: str | Path, include_hidden: bool = False, max_files: int = 20000) -> ScanRequest:
        return ScanRequest(
            repo_root=Path(repo_root),
            ignored_directories=set(self.ignored_directories),
            ignored_suffixes=set(self.ignored_suffixes),
            include_hidden=include_hidden,
            max_files=max_files,
        ).validate()

    def scan_paths(self, request: ScanRequest) -> RepositorySnapshot:
        request.validate()
        repo_root = request.repo_root
        discovered_files: list[str] = []
        discovered_directories: list[str] = []
        truncated = False

        for path in sorted(repo_root.rglob("*")):
            ensure_inside_root(repo_root, path, reason="repository scan")
            if not request.include_hidden and self._is_hidden(path, repo_root):
                continue
            if path.is_dir():
                if path.name in request.ignored_directories:
                    continue
                discovered_directories.append(path.relative_to(repo_root).as_posix())
                continue
            if self._should_skip_file(path, request):
                continue
            discovered_files.append(path.relative_to(repo_root).as_posix())
            if len(discovered_files) >= request.max_files:
                truncated = True
                break

        return RepositorySnapshot(
            repo_root=str(repo_root),
            discovered_files=discovered_files,
            discovered_directories=discovered_directories,
            truncated=truncated,
        )

    def scan_repository(self, repo_root: str) -> ScanResult:
        request = self.build_request(repo_root)
        snapshot = self.scan_paths(request)
        warnings: list[str] = []
        if snapshot.truncated:
            warnings.append("repository scan truncated by max_files limit")

        return ScanResult(
            repo_root=snapshot.repo_root,
            scan_id=f"scan::{Path(snapshot.repo_root).name}",
            artifact_findings=[],
            security_findings=[],
            stats=snapshot.to_stats(),
            warnings=warnings,
        ).validate()

    def _should_skip_file(self, path: Path, request: ScanRequest) -> bool:
        parts = {part for part in path.parts}
        if parts & request.ignored_directories:
            return True
        if path.suffix.lower() in request.ignored_suffixes:
            return True
        return False

    @staticmethod
    def _is_hidden(path: Path, repo_root: Path) -> bool:
        try:
            rel_parts = path.relative_to(repo_root).parts
        except ValueError:
            return False
        return any(part.startswith(".") for part in rel_parts if part not in {".", ".."})
