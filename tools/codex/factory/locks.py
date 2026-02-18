from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .common import RUNS_DIR, ensure_dir, iso_utc


class LockAcquisitionError(RuntimeError):
    pass


@dataclass
class FileLock:
    path: Path
    owner: str
    metadata: dict[str, Any]
    acquired: bool = False

    def acquire(self) -> "FileLock":
        ensure_dir(self.path.parent)
        payload = {
            "owner": self.owner,
            "pid": os.getpid(),
            "ts_utc": iso_utc(),
            "metadata": dict(self.metadata),
        }
        try:
            fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise LockAcquisitionError(f"lock already held: {self.path.as_posix()}") from exc
        try:
            os.write(fd, (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8"))
        finally:
            os.close(fd)
        self.acquired = True
        return self

    def release(self) -> None:
        if not self.acquired:
            return
        if self.path.exists():
            self.path.unlink()
        self.acquired = False

    def __enter__(self) -> "FileLock":
        return self.acquire()

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.release()
        return False


def run_locks_dir(run_id: str) -> Path:
    return RUNS_DIR / run_id / "locks"


def run_lock_path(run_id: str) -> Path:
    return run_locks_dir(run_id) / "run.lock"


def worker_lock_path(run_id: str, worker: str) -> Path:
    return run_locks_dir(run_id) / f"{worker}.lock"


def acquire_run_lock(run_id: str, *, owner: str) -> FileLock:
    return FileLock(path=run_lock_path(run_id), owner=owner, metadata={"run_id": run_id}).acquire()


def acquire_worker_lock(run_id: str, worker: str, *, owner: str) -> FileLock:
    return FileLock(
        path=worker_lock_path(run_id, worker),
        owner=owner,
        metadata={"run_id": run_id, "worker": worker},
    ).acquire()

