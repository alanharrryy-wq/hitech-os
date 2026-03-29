"""Project-scoped lock manager for one-button sessions.

The lock model follows the v1.2 contract:
- same host + live PID + heartbeat inside TTL => live lock
- same host + dead PID + expired heartbeat => stale lock
- different host + TTL not expired => assume live
- different host + TTL expired => stale-safe candidate

No external dependencies are introduced. The lock file is JSON and acquisition
uses an exclusive create where possible.
"""

from __future__ import annotations

import json
import os
import socket
import time
import uuid
from contextlib import AbstractContextManager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


class SessionLockError(Exception):
    """Base exception for lock operations."""


@dataclass(frozen=True)
class LockEvaluation:
    lock_path: Path
    lock_present: bool
    status: str
    reason: str
    host_matches: bool
    pid_alive: Optional[bool]
    ttl_seconds: int
    heartbeat_age_seconds: Optional[int]
    payload: Optional[Dict[str, Any]]


@dataclass(frozen=True)
class LockAcquireResult:
    lock_id: str
    lock_path: Path
    session_id: str
    acquired: bool
    reused_stale_lock: bool
    evaluation: LockEvaluation


class SessionLockHandle(AbstractContextManager['SessionLockHandle']):
    def __init__(self, manager: 'SessionLockManager', result: LockAcquireResult) -> None:
        self._manager = manager
        self.result = result
        self._released = False

    def heartbeat(self) -> None:
        if not self._released:
            self._manager.heartbeat(self.result)

    def release(self) -> None:
        if not self._released:
            self._manager.release(self.result)
            self._released = True

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()
        return None


class SessionLockManager:
    def __init__(self, lock_path: Path, ttl_seconds: int = 60, heartbeat_interval_seconds: int = 15) -> None:
        self.lock_path = lock_path
        self.ttl_seconds = int(ttl_seconds)
        self.heartbeat_interval_seconds = int(heartbeat_interval_seconds)
        self.current_host = socket.gethostname()
        self.current_pid = os.getpid()

    def acquire(self, *, session_id: str, project_id: str, force_lock_steal: bool = False) -> SessionLockHandle:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        evaluation = self.inspect_lock()
        reused_stale_lock = False

        if evaluation.lock_present:
            if evaluation.status == 'live':
                raise SessionLockError(
                    f"Project lock is already live at {self.lock_path}: {evaluation.reason}"
                )
            if evaluation.status in {'stale', 'stale_safe_candidate'}:
                if force_lock_steal and evaluation.status not in {'stale', 'stale_safe_candidate'}:
                    raise SessionLockError('force_lock_steal was requested for a lock that is not stale.')
                try:
                    self.lock_path.unlink(missing_ok=True)
                except TypeError:
                    if self.lock_path.exists():
                        self.lock_path.unlink()
                reused_stale_lock = True
            else:
                raise SessionLockError(
                    f"Project lock cannot be acquired because its state is ambiguous: {evaluation.reason}"
                )

        lock_id = f'lock_{uuid.uuid4().hex}'
        payload = self._build_payload(lock_id=lock_id, session_id=session_id, project_id=project_id)
        self._atomic_write_new_lock(payload)
        result = LockAcquireResult(
            lock_id=lock_id,
            lock_path=self.lock_path,
            session_id=session_id,
            acquired=True,
            reused_stale_lock=reused_stale_lock,
            evaluation=evaluation,
        )
        return SessionLockHandle(self, result)

    def inspect_lock(self) -> LockEvaluation:
        if not self.lock_path.exists():
            return LockEvaluation(
                lock_path=self.lock_path,
                lock_present=False,
                status='absent',
                reason='Lock file does not exist.',
                host_matches=False,
                pid_alive=None,
                ttl_seconds=self.ttl_seconds,
                heartbeat_age_seconds=None,
                payload=None,
            )
        payload = self._read_json(self.lock_path)
        host = str(payload.get('host', ''))
        pid = int(payload.get('pid', 0) or 0)
        heartbeat_at = str(payload.get('heartbeat_at_utc', payload.get('acquired_at_utc', '')))
        heartbeat_age = self._seconds_since_iso(heartbeat_at)
        host_matches = host.lower() == self.current_host.lower()
        pid_alive = self._is_pid_alive(pid) if host_matches and pid > 0 else None
        ttl = int(payload.get('ttl_seconds', self.ttl_seconds) or self.ttl_seconds)
        ttl_expired = heartbeat_age is not None and heartbeat_age > ttl

        if host_matches:
            if pid_alive and not ttl_expired:
                return LockEvaluation(self.lock_path, True, 'live', 'Same host, live PID, heartbeat inside TTL.', True, True, ttl, heartbeat_age, payload)
            if (pid_alive is False) and ttl_expired:
                return LockEvaluation(self.lock_path, True, 'stale', 'Same host, dead PID, heartbeat expired.', True, False, ttl, heartbeat_age, payload)
            if pid_alive and ttl_expired:
                return LockEvaluation(self.lock_path, True, 'live', 'Same host, live PID, heartbeat expired but process is still alive.', True, True, ttl, heartbeat_age, payload)
            return LockEvaluation(self.lock_path, True, 'ambiguous', 'Same host but PID liveness / heartbeat does not satisfy live or stale rules.', True, pid_alive, ttl, heartbeat_age, payload)

        if not ttl_expired:
            return LockEvaluation(self.lock_path, True, 'live', 'Different host and TTL not expired; assuming lock is live.', False, None, ttl, heartbeat_age, payload)
        return LockEvaluation(self.lock_path, True, 'stale_safe_candidate', 'Different host and TTL expired; safe to treat as stale-safe candidate.', False, None, ttl, heartbeat_age, payload)

    def heartbeat(self, result: LockAcquireResult) -> None:
        if not self.lock_path.exists():
            raise SessionLockError(f'Cannot heartbeat missing lock file: {self.lock_path}')
        payload = self._read_json(self.lock_path)
        if payload.get('lock_id') != result.lock_id or payload.get('session_id') != result.session_id:
            raise SessionLockError('Cannot heartbeat lock because lock ownership changed.')
        payload['heartbeat_at_utc'] = self._utc_now_iso()
        self._overwrite_json(self.lock_path, payload)

    def release(self, result: LockAcquireResult) -> None:
        if not self.lock_path.exists():
            return
        payload = self._read_json(self.lock_path)
        if payload.get('lock_id') != result.lock_id or payload.get('session_id') != result.session_id:
            return
        try:
            self.lock_path.unlink(missing_ok=True)
        except TypeError:
            if self.lock_path.exists():
                self.lock_path.unlink()

    def _atomic_write_new_lock(self, payload: Dict[str, Any]) -> None:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        fd = None
        try:
            fd = os.open(str(self.lock_path), flags)
            raw = json.dumps(payload, indent=2, ensure_ascii=False).encode('utf-8')
            os.write(fd, raw)
        except FileExistsError as exc:
            raise SessionLockError(f'Lock file already exists at {self.lock_path}') from exc
        finally:
            if fd is not None:
                os.close(fd)

    def _build_payload(self, *, lock_id: str, session_id: str, project_id: str) -> Dict[str, Any]:
        timestamp = self._utc_now_iso()
        return {
            'lock_id': lock_id,
            'session_id': session_id,
            'project_id': project_id,
            'pid': self.current_pid,
            'host': self.current_host,
            'acquired_at_utc': timestamp,
            'heartbeat_at_utc': timestamp,
            'ttl_seconds': self.ttl_seconds,
        }

    @staticmethod
    def _read_json(path: Path) -> Dict[str, Any]:
        with path.open('r', encoding='utf-8') as fh:
            return json.load(fh)

    @staticmethod
    def _overwrite_json(path: Path, payload: Dict[str, Any]) -> None:
        tmp_path = path.with_suffix(path.suffix + '.tmp')
        with tmp_path.open('w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        tmp_path.replace(path)

    @staticmethod
    def _utc_now_iso() -> str:
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    @staticmethod
    def _seconds_since_iso(value: str) -> Optional[int]:
        try:
            if not value:
                return None
            if value.endswith('Z'):
                value = value[:-1] + '+00:00'
            parsed = __import__('datetime').datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=__import__('datetime').timezone.utc)
            now = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
            return max(0, int((now - parsed).total_seconds()))
        except Exception:
            return None

    @staticmethod
    def _is_pid_alive(pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True
