#!/usr/bin/env python3
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from tools.hos._core.stable_json import load_json, write_json

from .config import SentinelConfig
from .utils import now_utc_iso


def _to_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if pid == os.getpid():
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _resolve_lock_path(config: SentinelConfig) -> Path:
    raw = Path(config.lock_path)
    if raw.is_absolute():
        return raw.resolve()
    return (config.repo_root / raw).resolve()


@dataclass(frozen=True)
class GuardianLock:
    acquired: bool
    lock_path: Path
    token: str
    owner: dict[str, Any]
    reason: str


def acquire_guardian_lock(config: SentinelConfig, owner_label: str = "guardian") -> GuardianLock:
    lock_path = _resolve_lock_path(config)
    now_epoch = int(time.time())
    stale_seconds = max(60, int(config.lock_stale_seconds))
    current_owner = {
        "pid": os.getpid(),
        "token": uuid4().hex,
        "owner": str(owner_label),
        "startedAt": now_utc_iso(),
        "epoch": now_epoch,
    }

    existing: dict[str, Any] = {}
    if lock_path.exists():
        try:
            payload = load_json(lock_path)
            if isinstance(payload, dict):
                existing = payload
        except (OSError, ValueError):
            existing = {}

    if existing:
        existing_epoch = _to_int(existing.get("epoch"), fallback=0)
        existing_pid = _to_int(existing.get("pid"), fallback=0)
        existing_age = max(0, now_epoch - existing_epoch) if existing_epoch > 0 else stale_seconds + 1
        if _pid_is_alive(existing_pid) and existing_age <= stale_seconds:
            return GuardianLock(
                acquired=False,
                lock_path=lock_path,
                token="",
                owner=existing,
                reason=f"active lock held by pid={existing_pid} age={existing_age}s",
            )

    write_json(lock_path, current_owner, indent=2, sort_keys=True)
    return GuardianLock(
        acquired=True,
        lock_path=lock_path,
        token=str(current_owner["token"]),
        owner=current_owner,
        reason="acquired",
    )


def release_guardian_lock(lock: GuardianLock) -> bool:
    if not lock.acquired:
        return False
    if not lock.lock_path.exists():
        return True
    try:
        payload = load_json(lock.lock_path)
    except (OSError, ValueError):
        payload = {}
    if isinstance(payload, dict):
        payload_token = str(payload.get("token", ""))
        payload_pid = _to_int(payload.get("pid"), fallback=-1)
        if payload_token != lock.token or payload_pid != os.getpid():
            return False
    try:
        lock.lock_path.unlink(missing_ok=True)
        return True
    except OSError:
        return False
