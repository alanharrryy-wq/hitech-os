from __future__ import annotations

import sys
import time


class Progress:
    def __init__(self, total: int):
        self.total = max(1, total)
        self.current = 0
        self.started = time.monotonic()

    def step(self, label: str) -> None:
        self.current = min(self.total, self.current + 1)
        pct = int((self.current / self.total) * 100)
        remaining = 100 - pct
        elapsed = time.monotonic() - self.started
        print(f"[{pct:3d}% | falta {remaining:3d}% | {elapsed:6.1f}s] {label}", file=sys.stderr, flush=True)
