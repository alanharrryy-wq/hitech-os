from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, QObject

from application.session_manager import SessionManager
from domain import AppEvent
from infrastructure.event_bus import EventBus


class FileWatcherService(QObject):
    def __init__(self, event_bus: EventBus, session_manager: SessionManager) -> None:
        super().__init__()
        self._event_bus = event_bus
        self._session_manager = session_manager
        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._on_path_changed)
        self._watcher.directoryChanged.connect(self._on_path_changed)
        self._session_paths: dict[str, set[str]] = {}
        self._path_sessions: dict[str, set[str]] = {}

    def watch_session(self, session_id: str) -> None:
        session = self._session_manager.get(session_id)
        if session is None:
            return

        self.unwatch_session(session_id)
        watch_paths = self._collect_existing_paths(session.scope.targets)
        self._session_paths[session_id] = watch_paths

        for path in watch_paths:
            owners = self._path_sessions.setdefault(path, set())
            owners.add(session_id)

        if watch_paths:
            self._watcher.addPaths(sorted(watch_paths))

    def unwatch_session(self, session_id: str) -> None:
        existing = self._session_paths.pop(session_id, set())
        for path in existing:
            owners = self._path_sessions.get(path)
            if owners is None:
                continue
            owners.discard(session_id)
            if owners:
                continue

            self._path_sessions.pop(path, None)
            if path in self._watcher.files() or path in self._watcher.directories():
                self._watcher.removePath(path)

    def _collect_existing_paths(self, targets: list[str]) -> set[str]:
        result: set[str] = set()
        for raw in targets:
            path = Path(raw)
            if path.exists():
                result.add(str(path.resolve()))
        return result

    def _on_path_changed(self, path: str) -> None:
        owners = self._path_sessions.get(path, set())
        for session_id in owners:
            session = self._session_manager.mark_stale(session_id)
            if session is None:
                continue

            self._event_bus.emit(
                AppEvent(
                    name="filesystem_changed",
                    session_id=session_id,
                    payload={"path": path},
                )
            )
            self._event_bus.emit(
                AppEvent(
                    name="session_marked_stale",
                    session_id=session_id,
                    payload={"path": path},
                )
            )
