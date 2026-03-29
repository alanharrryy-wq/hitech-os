from __future__ import annotations

import contextlib
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator

from .paths import GuardianPaths
from .policy import GuardianPolicy



def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


@dataclass
class StateStore:
    paths: GuardianPaths
    policy: GuardianPolicy

    def __post_init__(self) -> None:
        self.resolved_tools_path = self.paths.state_dir / 'resolved_tools.json'
        self.boot_state_path = self.paths.state_dir / 'boot_state.json'
        self.engine_status_path = self.paths.state_dir / 'engine_status_latest.json'
        self.repo_analyzer_status_path = self.paths.state_dir / 'repo_analyzer_status.json'
        self.last_actions_path = self.paths.state_dir / 'last_actions.jsonl'
        self.engine_log_path = self.paths.logs_dir / 'engine_guardian.log'
        self.repo_analyzer_log_path = self.paths.logs_dir / 'repo_analyzer_guardian.log'

    def write_json(self, path: Path, payload: Dict[str, Any]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + '\n', encoding='utf-8')
        return path

    def read_json(self, path: Path, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not path.exists():
            return dict(default or {})
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return dict(default or {})

    def append_jsonl(self, path: Path, payload: Dict[str, Any]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a', encoding='utf-8', newline='\n') as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + '\n')
        return path

    def seed_runtime_files(self) -> None:
        self.paths.ensure_runtime_layout()
        defaults = {
            self.resolved_tools_path: {},
            self.boot_state_path: {
                'attempt_count': 0,
                'last_attempt_utc': None,
                'window_hours': self.policy.boot_window_hours,
                'updated_at_utc': utc_now_iso(),
            },
            self.engine_status_path: {
                'status': 'unknown',
                'engine_public_healthy': False,
                'timestamp_utc': utc_now_iso(),
            },
            self.repo_analyzer_status_path: {
                'status': 'unknown',
                'healthy': False,
                'timestamp_utc': utc_now_iso(),
            },
        }
        for path, payload in defaults.items():
            if not path.exists():
                self.write_json(path, payload)
        self.last_actions_path.parent.mkdir(parents=True, exist_ok=True)
        self.last_actions_path.touch(exist_ok=True)
        self.engine_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine_log_path.touch(exist_ok=True)
        self.repo_analyzer_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.repo_analyzer_log_path.touch(exist_ok=True)

    def write_snapshot(self, name: str, payload: Dict[str, Any]) -> Path:
        safe_name = ''.join(ch if ch.isalnum() or ch in ('_', '-') else '_' for ch in name).strip('_') or 'snapshot'
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        path = self.paths.snapshots_dir / f'{safe_name}_{stamp}.json'
        return self.write_json(path, payload)

    def register_boot_attempt(self, reason: str) -> Dict[str, Any]:
        self.seed_runtime_files()
        current = self.read_json(self.boot_state_path, {})
        last_attempt = current.get('last_attempt_utc')
        if self.policy.is_boot_window_expired(last_attempt):
            attempt_count = 0
        else:
            attempt_count = int(current.get('attempt_count', 0))
        attempt_count += 1
        payload = {
            'reason': reason,
            'attempt_count': attempt_count,
            'last_attempt_utc': utc_now_iso(),
            'window_hours': self.policy.boot_window_hours,
            'updated_at_utc': utc_now_iso(),
        }
        self.write_json(self.boot_state_path, payload)
        return payload

    def append_log_line(self, log_path: Path, message: str) -> None:
        line = f"{utc_now_iso()} {message}\n"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open('a', encoding='utf-8', newline='\n') as handle:
            handle.write(line)

    @contextlib.contextmanager
    def locked(self, name: str = 'global') -> Iterator[Path]:
        self.seed_runtime_files()
        lock_path = self.paths.locks_dir / f'{name}.lock'
        payload = {'name': name, 'timestamp_utc': utc_now_iso(), 'pid': os.getpid()}
        ttl = self.policy.global_lock_ttl_seconds
        while True:
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, 'w', encoding='utf-8') as handle:
                    handle.write(json.dumps(payload, ensure_ascii=False))
                break
            except FileExistsError:
                stale = False
                try:
                    current = json.loads(lock_path.read_text(encoding='utf-8'))
                    stamp = current.get('timestamp_utc')
                    if stamp:
                        created = datetime.fromisoformat(stamp.replace('Z', '+00:00')).timestamp()
                        stale = (time.time() - created) > ttl
                except Exception:
                    stale = True
                if stale:
                    lock_path.unlink(missing_ok=True)
                    continue
                raise RuntimeError(f'Another Engine Guardian run holds lock {lock_path.name}.')
        try:
            yield lock_path
        finally:
            lock_path.unlink(missing_ok=True)
