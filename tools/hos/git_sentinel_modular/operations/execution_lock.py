from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(slots=True)
class ExecutionLock:
    lock_path: Path

    def acquire(self, owner: str) -> bool:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        if self.lock_path.exists():
            return False
        payload = {
            "owner": owner,
            "created_at": _iso_now(),
        }
        self.lock_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return True

    def read(self) -> dict:
        if not self.lock_path.exists():
            return {}
        return json.loads(self.lock_path.read_text(encoding="utf-8"))

    def release(self) -> None:
        if self.lock_path.exists():
            self.lock_path.unlink()

    def __enter__(self):
        ok = self.acquire("context-manager")
        if not ok:
            raise RuntimeError(f"Execution lock already exists: {self.lock_path}")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
        return False
