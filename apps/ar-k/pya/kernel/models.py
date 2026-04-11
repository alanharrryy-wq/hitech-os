from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class EngineRunResult:
    execution_summary: dict[str, Any]
    notes: list[str] = field(default_factory=list)


class Engine(Protocol):
    engine_id: str
    stage: str
    manifest: dict[str, Any]

    def run(self, context: "RuntimeContext") -> EngineRunResult:
        ...
