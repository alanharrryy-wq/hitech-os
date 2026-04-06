
from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


@dataclass(slots=True)
class TaskOutcome:
    task_id: str
    payload: Any


@dataclass(slots=True)
class TaskError:
    task_id: str
    message: str
    traceback_text: str


class _TaskSignals(QObject):
    started = Signal(str)
    result = Signal(object)
    error = Signal(object)
    finished = Signal(str)


class _TaskRunnable(QRunnable):
    def __init__(self, task_id: str, fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        super().__init__()
        self.task_id = task_id
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = _TaskSignals()
        self.setAutoDelete(True)

    def run(self) -> None:
        self.signals.started.emit(self.task_id)
        try:
            payload = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(TaskOutcome(self.task_id, payload))
        except Exception as exc:  # noqa: BLE001
            self.signals.error.emit(
                TaskError(
                    task_id=self.task_id,
                    message=str(exc),
                    traceback_text=traceback.format_exc(limit=20),
                )
            )
        finally:
            self.signals.finished.emit(self.task_id)


class EngineTaskRunner(QObject):
    taskStarted = Signal(str)
    taskResult = Signal(object)
    taskError = Signal(object)
    taskFinished = Signal(str)

    def __init__(self, parent: QObject | None = None, *, max_threads: int = 2) -> None:
        super().__init__(parent)
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(max(1, int(max_threads)))

    def submit(self, task_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        runnable = _TaskRunnable(task_id, fn, args, kwargs)
        runnable.signals.started.connect(self.taskStarted)
        runnable.signals.result.connect(self.taskResult)
        runnable.signals.error.connect(self.taskError)
        runnable.signals.finished.connect(self.taskFinished)
        self._pool.start(runnable)
