from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..shared.status_payloads import utc_now_iso

@dataclass(slots=True)
class RunMetrics:
    run_id: str
    started_at: str = field(default_factory=utc_now_iso)
    counters: dict[str, int] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)

    def increment(self, key: str, amount: int = 1) -> None:
        self.counters[key] = self.counters.get(key, 0) + amount

    def set_detail(self, key: str, value: Any) -> None:
        self.details[key] = value

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return target
