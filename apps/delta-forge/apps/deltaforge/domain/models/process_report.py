from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


TAIL_LIMIT = 20


@dataclass(slots=True)
class ProcessReport:
    engine_name: str
    mode: str
    stdout_tail: list[str] = field(default_factory=list)
    stderr_tail: list[str] = field(default_factory=list)
    exit_code: int | None = None

    def append_stdout(self, lines: Iterable[str]) -> None:
        self.stdout_tail = _append_tail(self.stdout_tail, lines)

    def append_stderr(self, lines: Iterable[str]) -> None:
        self.stderr_tail = _append_tail(self.stderr_tail, lines)

    def as_dict(self) -> dict[str, object]:
        return {
            "engine_name": self.engine_name,
            "mode": self.mode,
            "stdout_tail": list(self.stdout_tail),
            "stderr_tail": list(self.stderr_tail),
            "exit_code": self.exit_code,
        }


def _append_tail(current: list[str], lines: Iterable[str]) -> list[str]:
    merged = [str(item) for item in current]
    merged.extend(str(item) for item in lines)
    if len(merged) <= TAIL_LIMIT:
        return merged
    return merged[-TAIL_LIMIT:]
