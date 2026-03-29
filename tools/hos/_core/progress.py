#!/usr/bin/env python3
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from time import monotonic


@dataclass
class Progress:
    total: int
    label: str = "progress"
    stream: object = sys.stdout
    _current: int = 0
    _start: float = field(default_factory=monotonic)

    def _tty(self) -> bool:
        isatty = getattr(self.stream, "isatty", None)
        return bool(isatty and isatty())

    def _line(self, final: bool = False) -> str:
        total = max(1, self.total)
        percent = min(100.0, (self._current / total) * 100.0)
        elapsed = max(0.0, monotonic() - self._start)
        return (
            f"{self.label}: {self._current}/{total} "
            f"({percent:6.2f}%) elapsed={elapsed:7.2f}s"
            + ("\n" if final or not self._tty() else "\r")
        )

    def update(self, current: int | None = None, increment: int = 1) -> None:
        if current is None:
            self._current += increment
        else:
            self._current = current
        self._current = max(0, min(self._current, self.total))
        self.stream.write(self._line())
        self.stream.flush()

    def done(self) -> None:
        self._current = self.total
        self.stream.write(self._line(final=True))
        self.stream.flush()

