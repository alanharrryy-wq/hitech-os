from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from app.backend import AnalyzerBackend


class IndexWorker(QObject):
    progress = Signal(str)
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, backend: AnalyzerBackend, repo_path: str, include_hidden: bool) -> None:
        super().__init__()
        self.backend = backend
        self.repo_path = repo_path
        self.include_hidden = include_hidden

    @Slot()
    def run(self) -> None:
        try:
            payload = self.backend.index_repo(
                Path(self.repo_path),
                include_hidden=self.include_hidden,
                progress=self.progress.emit,
            )
            self.finished.emit(payload)
        except Exception as e:
            self.error.emit(str(e))


class SearchWorker(QObject):
    progress = Signal(str)
    finished = Signal(object)
    error = Signal(str)

    def __init__(
        self,
        backend: AnalyzerBackend,
        index_data: dict,
        query: str,
        folder: str,
        ext_filter: str,
        sort_mode: str,
        case_sensitive: bool,
        is_regex: bool,
        whole_word: bool,
        names_only: bool,
        max_results: int,
    ) -> None:
        super().__init__()
        self.backend = backend
        self.index_data = index_data
        self.query = query
        self.folder = folder
        self.ext_filter = ext_filter
        self.sort_mode = sort_mode
        self.case_sensitive = case_sensitive
        self.is_regex = is_regex
        self.whole_word = whole_word
        self.names_only = names_only
        self.max_results = max_results

    @Slot()
    def run(self) -> None:
        try:
            results = self.backend.search(
                self.index_data,
                self.query,
                self.folder,
                self.ext_filter,
                self.sort_mode,
                self.case_sensitive,
                self.is_regex,
                self.whole_word,
                self.names_only,
                self.max_results,
                progress=self.progress.emit,
            )
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))
