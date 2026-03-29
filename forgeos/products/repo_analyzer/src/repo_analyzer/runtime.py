from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol

from .models import RepoAnalyzerState, RepositorySummary, SearchMatch

_SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
}


class HistoryRunsWriter(Protocol):
    def append(
        self,
        run_id: str,
        producer: str,
        status: str,
        actor: str,
        correlation_id: str,
        details: dict[str, str] | None = None,
    ) -> object:
        pass


class RepoAnalyzerRuntime:
    """Migrated Repo Analyzer runtime with product-local domain authority."""

    product_id = "repo_analyzer"
    contribution_id = "contrib.repo_analyzer.main_surface"
    slot_id = "primary_workspace"
    surface_kind = "panel"

    def __init__(self, history_runs: HistoryRunsWriter | None = None) -> None:
        self._history_runs = history_runs
        self._state = RepoAnalyzerState.REGISTERED
        self._root_path: Path | None = None
        self._last_summary: RepositorySummary | None = None

    @property
    def state(self) -> RepoAnalyzerState:
        return self._state

    @property
    def last_summary(self) -> RepositorySummary | None:
        return self._last_summary

    def prepare(self, root_path: str) -> RepoAnalyzerState:
        self._root_path = Path(root_path).resolve()
        self._state = RepoAnalyzerState.PREPARED
        return self._state

    def activate(self) -> RepoAnalyzerState:
        self._require_state(RepoAnalyzerState.PREPARED, RepoAnalyzerState.SUSPENDED)
        self._state = RepoAnalyzerState.ACTIVE
        return self._state

    def suspend(self) -> RepoAnalyzerState:
        self._require_state(RepoAnalyzerState.ACTIVE)
        self._state = RepoAnalyzerState.SUSPENDED
        return self._state

    def dispose(self) -> RepoAnalyzerState:
        if self._state is RepoAnalyzerState.DISPOSED:
            return self._state
        self._state = RepoAnalyzerState.DISPOSING
        self._last_summary = None
        self._state = RepoAnalyzerState.DISPOSED
        return self._state

    def analyze_repository(
        self,
        actor: str,
        correlation_id: str,
    ) -> RepositorySummary:
        self._require_state(RepoAnalyzerState.ACTIVE)
        root = self._require_root()

        total_files = 0
        total_lines = 0
        extension_counts: dict[str, int] = {}

        for file_path in self._iter_files(root):
            if not self._is_text_file(file_path):
                continue
            total_files += 1
            extension = file_path.suffix.lower() or "<none>"
            extension_counts[extension] = extension_counts.get(extension, 0) + 1
            total_lines += self._count_lines(file_path)

        summary = RepositorySummary(
            root_path=str(root),
            total_files=total_files,
            total_lines=total_lines,
            generated_at_utc=datetime.now(tz=timezone.utc).isoformat(),
            extension_counts=dict(sorted(extension_counts.items())),
        )
        self._last_summary = summary

        if self._history_runs is not None:
            run_id = f"repo_analyzer:{summary.generated_at_utc}"
            self._history_runs.append(
                run_id=run_id,
                producer=self.product_id,
                status="finished",
                actor=actor,
                correlation_id=correlation_id,
                details={
                    "root_path": summary.root_path,
                    "total_files": str(summary.total_files),
                    "total_lines": str(summary.total_lines),
                },
            )
        return summary

    def search(self, pattern: str, limit: int = 50) -> list[SearchMatch]:
        self._require_state(RepoAnalyzerState.ACTIVE)
        root = self._require_root()
        needle = pattern.lower()
        results: list[SearchMatch] = []
        for file_path in self._iter_files(root):
            if not self._is_text_file(file_path):
                continue
            try:
                with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
                    for line_number, raw_line in enumerate(handle, start=1):
                        text = raw_line.rstrip("\n")
                        if needle in text.lower():
                            results.append(
                                SearchMatch(
                                    file_path=str(file_path),
                                    line_number=line_number,
                                    line_text=text,
                                )
                            )
                            if len(results) >= limit:
                                return results
            except OSError:
                continue
        return results

    def preview_file(self, file_path: str, max_lines: int = 80) -> list[str]:
        self._require_state(RepoAnalyzerState.ACTIVE)
        root = self._require_root()
        target = Path(file_path).resolve()
        if root not in target.parents and target != root:
            raise ValueError("file path must be inside the prepared repository root")
        lines: list[str] = []
        with target.open("r", encoding="utf-8", errors="ignore") as handle:
            for _, raw_line in enumerate(handle, start=1):
                lines.append(raw_line.rstrip("\n"))
                if len(lines) >= max_lines:
                    break
        return lines

    def contribution_actions(self) -> dict[str, Callable[[], object]]:
        return {"refresh_summary": self._refresh_summary_action}

    def _refresh_summary_action(self) -> dict[str, object]:
        summary = self._last_summary
        if summary is None:
            summary = self.analyze_repository(
                actor="repo_analyzer",
                correlation_id="repo-analyzer-refresh",
            )
        return {
            "root_path": summary.root_path,
            "total_files": summary.total_files,
            "total_lines": summary.total_lines,
            "extension_counts": summary.extension_counts,
            "generated_at_utc": summary.generated_at_utc,
        }

    def _iter_files(self, root: Path) -> list[Path]:
        paths: list[Path] = []
        for path in root.rglob("*"):
            if path.is_dir() and path.name in _SKIP_DIRS:
                continue
            if not path.is_file():
                continue
            if any(part in _SKIP_DIRS for part in path.parts):
                continue
            paths.append(path)
        return paths

    def _require_state(self, *states: RepoAnalyzerState) -> None:
        if self._state not in states:
            expected = ", ".join(state.value for state in states)
            raise RuntimeError(
                f"invalid repo_analyzer state '{self._state.value}', expected one of: {expected}"
            )

    def _require_root(self) -> Path:
        if self._root_path is None:
            raise RuntimeError("repo_analyzer runtime has no prepared root path")
        return self._root_path

    @staticmethod
    def _is_text_file(path: Path) -> bool:
        binary_ext = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".ico",
            ".zip",
            ".gz",
            ".tar",
            ".7z",
            ".pdf",
            ".woff",
            ".woff2",
            ".ttf",
            ".otf",
            ".mp4",
            ".mp3",
            ".wav",
            ".exe",
            ".dll",
            ".so",
            ".dylib",
        }
        return path.suffix.lower() not in binary_ext

    @staticmethod
    def _count_lines(path: Path) -> int:
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                return sum(1 for _ in handle)
        except OSError:
            return 0
