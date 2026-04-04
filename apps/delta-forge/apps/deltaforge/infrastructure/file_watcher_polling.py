from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Any, Callable


ChangeHandler = Callable[[list[dict[str, object]]], None]


class FileWatcherPolling:
    """Polling watcher that only detects and signals changes."""

    def __init__(
        self,
        *,
        interval_seconds: float = 1.0,
        event_bus: Any | None = None,
        event_name: str = "filesystem_changed",
    ) -> None:
        self._interval_seconds = float(interval_seconds)
        self._event_bus = event_bus
        self._event_name = event_name

        self._lock = threading.RLock()
        self._roots: set[Path] = set()
        self._snapshot: dict[str, dict[str, object]] = {}
        self._callbacks: list[ChangeHandler] = []

        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def watch(self, *paths: str | Path) -> tuple[str, ...]:
        with self._lock:
            for path in paths:
                self._roots.add(self._normalize_path(path))
            self._snapshot = self._collect_snapshot(self._roots)
            return self.watched_paths()

    def unwatch(self, *paths: str | Path) -> tuple[str, ...]:
        to_remove = {self._normalize_path(path) for path in paths}
        with self._lock:
            self._roots = {root for root in self._roots if root not in to_remove}
            self._snapshot = self._collect_snapshot(self._roots)
            return self.watched_paths()

    def watched_paths(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(str(path) for path in self._roots))

    def subscribe(self, handler: ChangeHandler) -> Callable[[], None]:
        with self._lock:
            self._callbacks.append(handler)

        def _unsubscribe() -> None:
            with self._lock:
                self._callbacks = [existing for existing in self._callbacks if existing is not handler]

        return _unsubscribe

    def poll(self) -> list[dict[str, object]]:
        with self._lock:
            roots = set(self._roots)
            previous = dict(self._snapshot)

        current = self._collect_snapshot(roots)
        changes = self._diff(previous, current)

        with self._lock:
            self._snapshot = current

        if changes:
            self._publish(changes)

        return changes

    def start(self) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return

            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run_loop,
                name="deltaforge-file-watcher-polling",
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        thread = self._thread
        if thread is not None:
            thread.join(timeout=max(self._interval_seconds * 2.0, 0.1))
        self._thread = None

    def close(self) -> None:
        self.stop()
        with self._lock:
            self._roots.clear()
            self._snapshot.clear()
            self._callbacks.clear()

    def _run_loop(self) -> None:
        while not self._stop_event.wait(self._interval_seconds):
            self.poll()

    def _publish(self, changes: list[dict[str, object]]) -> None:
        with self._lock:
            callbacks = tuple(self._callbacks)

        for callback in callbacks:
            callback(changes)

        if self._event_bus is None:
            return

        emit = getattr(self._event_bus, "emit", None)
        if callable(emit):
            emit(self._event_name, changes)
            return

        publish = getattr(self._event_bus, "publish", None)
        if callable(publish):
            publish(self._event_name, changes)

    @staticmethod
    def _normalize_path(path: str | Path) -> Path:
        return Path(path).expanduser().resolve(strict=False)

    def _collect_snapshot(self, roots: set[Path]) -> dict[str, dict[str, object]]:
        snapshot: dict[str, dict[str, object]] = {}
        for root in roots:
            snapshot.update(self._collect_root(root))
        return snapshot

    def _collect_root(self, root: Path) -> dict[str, dict[str, object]]:
        collected: dict[str, dict[str, object]] = {}
        root_text = str(root)

        if not root.exists():
            return collected

        for path in self._iter_tree(root):
            try:
                stat = path.stat()
            except OSError:
                continue

            is_dir = path.is_dir()
            collected[str(path)] = {
                "is_dir": is_dir,
                "mtime_ns": getattr(stat, "st_mtime_ns", None),
                "size": None if is_dir else getattr(stat, "st_size", None),
                "root_path": root_text,
            }

        return collected

    def _iter_tree(self, root: Path):
        yield root
        if not root.is_dir():
            return

        stack = [root]
        while stack:
            current_dir = stack.pop()
            try:
                entries = list(os.scandir(current_dir))
            except OSError:
                continue

            for entry in entries:
                path = Path(entry.path)
                yield path
                if entry.is_dir(follow_symlinks=False):
                    stack.append(path)

    @staticmethod
    def _diff(
        previous: dict[str, dict[str, object]],
        current: dict[str, dict[str, object]],
    ) -> list[dict[str, object]]:
        changes: list[dict[str, object]] = []

        previous_paths = set(previous)
        current_paths = set(current)

        for path in sorted(current_paths - previous_paths):
            meta = current[path]
            changes.append(
                {
                    "path": path,
                    "change_type": "created",
                    "is_dir": meta["is_dir"],
                    "root_path": meta["root_path"],
                    "mtime_ns": meta["mtime_ns"],
                    "size": meta["size"],
                }
            )

        for path in sorted(previous_paths - current_paths):
            meta = previous[path]
            changes.append(
                {
                    "path": path,
                    "change_type": "deleted",
                    "is_dir": meta["is_dir"],
                    "root_path": meta["root_path"],
                    "mtime_ns": None,
                    "size": None,
                }
            )

        for path in sorted(previous_paths & current_paths):
            old = previous[path]
            new = current[path]
            if old.get("mtime_ns") != new.get("mtime_ns") or old.get("size") != new.get("size"):
                changes.append(
                    {
                        "path": path,
                        "change_type": "modified",
                        "is_dir": new["is_dir"],
                        "root_path": new["root_path"],
                        "mtime_ns": new["mtime_ns"],
                        "size": new["size"],
                    }
                )

        return changes
