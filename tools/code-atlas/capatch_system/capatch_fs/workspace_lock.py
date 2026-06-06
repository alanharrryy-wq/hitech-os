from __future__ import annotations

import json
import os
import socket
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from capatch_audit.renderers import read_json, sha256_file, write_json


DEFAULT_LOCK_STALE_SECONDS = 2 * 60 * 60
DEFAULT_WAIT_TIMEOUT_SECONDS = 8.0
DEFAULT_RETRY_INTERVAL_SECONDS = 0.2


@dataclass(slots=True)
class WorkspaceLock:
    root_dir: str
    lock_path: str
    owner_token: str
    acquired_at: str
    hostname: str
    pid: int
    stale_after_seconds: int
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema_version"] = "1.0.0"
        return payload

    def release(self) -> None:
        lock_path = Path(self.lock_path)
        current = read_json(lock_path, None)
        if isinstance(current, dict):
            if str(current.get("owner_token") or "") != self.owner_token:
                return
        try:
            lock_path.unlink()
        except FileNotFoundError:
            return

    def __enter__(self) -> "WorkspaceLock":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()


def _utc_now_iso() -> str:
    import datetime as _dt

    return _dt.datetime.now(_dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def _lock_dir(root_dir: Path) -> Path:
    return Path(root_dir).resolve() / "reports" / "locks"


def lock_path_for_root(root_dir: Path) -> Path:
    return _lock_dir(root_dir) / "workspace.lock.json"


def _read_lock(path_value: Path) -> dict[str, Any] | None:
    payload = read_json(path_value, None)
    return payload if isinstance(payload, dict) else None


def _lock_is_stale(path_value: Path, payload: dict[str, Any] | None, *, stale_after_seconds: int) -> bool:
    if not path_value.exists():
        return False
    try:
        age = time.time() - path_value.stat().st_mtime
    except Exception:
        age = 0.0
    if age >= max(1, int(stale_after_seconds)):
        return True
    if not isinstance(payload, dict):
        return False
    pid = int(payload.get("pid") or 0)
    if pid <= 0:
        return False
    if pid == os.getpid():
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            return False
        except Exception:
            return False
    return False


def force_release_workspace_lock(root_dir: Path, *, reason: str = "manual") -> dict[str, Any]:
    path_value = lock_path_for_root(root_dir)
    payload = _read_lock(path_value)
    released = False
    if path_value.exists():
        try:
            path_value.unlink()
            released = True
        except Exception:
            released = False
    return {
        "lock_path": str(path_value),
        "released": released,
        "reason": str(reason),
        "previous_owner": payload,
    }


def acquire_workspace_lock(
    root_dir: Path,
    *,
    owner_token: str,
    metadata: dict[str, Any] | None = None,
    stale_after_seconds: int = DEFAULT_LOCK_STALE_SECONDS,
    wait_timeout_seconds: float = DEFAULT_WAIT_TIMEOUT_SECONDS,
    retry_interval_seconds: float = DEFAULT_RETRY_INTERVAL_SECONDS,
) -> WorkspaceLock:
    root_dir = Path(root_dir).resolve()
    path_value = lock_path_for_root(root_dir)
    path_value.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    while True:
        existing = _read_lock(path_value)
        if existing is not None and _lock_is_stale(path_value, existing, stale_after_seconds=stale_after_seconds):
            try:
                path_value.unlink()
            except FileNotFoundError:
                pass
            except Exception:
                pass
            existing = None
        payload = {
            "schema_version": "1.0.0",
            "root_dir": str(root_dir),
            "owner_token": str(owner_token),
            "acquired_at": _utc_now_iso(),
            "hostname": socket.gethostname(),
            "pid": os.getpid(),
            "stale_after_seconds": int(stale_after_seconds),
            "metadata": dict(metadata or {}),
        }
        try:
            fd = os.open(str(path_value), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if (time.monotonic() - started) >= float(wait_timeout_seconds):
                raise TimeoutError(
                    f"workspace lock busy: {path_value} owner={existing or {}}"
                )
            time.sleep(max(0.05, float(retry_interval_seconds)))
            continue
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=True)
                handle.write("\n")
        except Exception:
            try:
                path_value.unlink()
            except Exception:
                pass
            raise
        return WorkspaceLock(
            root_dir=str(root_dir),
            lock_path=str(path_value),
            owner_token=str(owner_token),
            acquired_at=str(payload["acquired_at"]),
            hostname=str(payload["hostname"]),
            pid=int(payload["pid"]),
            stale_after_seconds=int(stale_after_seconds),
            metadata=dict(metadata or {}),
        )


def collect_target_snapshot(root_dir: Path, target_files: list[str]) -> dict[str, dict[str, Any]]:
    root_dir = Path(root_dir).resolve()
    snapshot: dict[str, dict[str, Any]] = {}
    for item in sorted({str(value).replace("\\", "/") for value in list(target_files or []) if str(value).strip()}):
        path_value = root_dir / item
        exists = path_value.exists()
        entry: dict[str, Any] = {
            "relative_path": item,
            "exists": bool(exists),
            "is_symlink": bool(path_value.is_symlink()) if exists else False,
            "resolved": str(path_value.resolve()) if exists else None,
            "sha256": sha256_file(path_value) if exists and path_value.is_file() else None,
            "size": path_value.stat().st_size if exists and path_value.is_file() else None,
            "mtime_ns": path_value.stat().st_mtime_ns if exists else None,
        }
        snapshot[item] = entry
    return snapshot


def diff_target_snapshot(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    keys = sorted(set(before) | set(after))
    for key in keys:
        left = dict(before.get(key) or {})
        right = dict(after.get(key) or {})
        if left == right:
            continue
        reason = "metadata_changed"
        if bool(left.get("exists")) != bool(right.get("exists")):
            reason = "existence_changed"
        elif left.get("sha256") != right.get("sha256"):
            reason = "hash_changed"
        elif left.get("mtime_ns") != right.get("mtime_ns"):
            reason = "mtime_changed"
        elif bool(left.get("is_symlink")) != bool(right.get("is_symlink")):
            reason = "symlink_changed"
        rows.append(
            {
                "relative_path": key,
                "reason": reason,
                "before": left,
                "after": right,
            }
        )
    return rows
