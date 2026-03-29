from __future__ import annotations

import json
import time
from pathlib import Path

from _test_support import OneButtonFrameworkTestCase


class TestSessionLock(OneButtonFrameworkTestCase):
    def setUp(self) -> None:
        framework_root = self.make_temp_framework()
        self.lock_path = framework_root / 'ops' / 'projects' / 'lock_demo' / 'state' / 'locks' / 'one_button.lock.json'
        lib_root = framework_root / 'tools' / 'execution_framework' / 'lib'
        import sys

        if str(lib_root) not in sys.path:
            sys.path.insert(0, str(lib_root))
        from session_lock import SessionLockManager  # type: ignore

        self.SessionLockManager = SessionLockManager

    def test_acquire_heartbeat_and_release_roundtrip(self) -> None:
        manager = self.SessionLockManager(self.lock_path, ttl_seconds=60, heartbeat_interval_seconds=15)
        with manager.acquire(session_id='sess_live', project_id='lock_demo') as handle:
            self.assertTrue(self.lock_path.exists())
            evaluation = manager.inspect_lock()
            self.assertEqual(evaluation.status, 'live')
            handle.heartbeat()
            payload = json.loads(self.lock_path.read_text(encoding='utf-8'))
            self.assertEqual(payload['session_id'], 'sess_live')
        self.assertFalse(self.lock_path.exists())

    def test_same_host_dead_pid_and_expired_heartbeat_is_stale(self) -> None:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            'lock_id': 'lock_dead',
            'session_id': 'sess_dead',
            'project_id': 'lock_demo',
            'pid': 999999,
            'host': self.SessionLockManager(self.lock_path).current_host,
            'acquired_at_utc': '2000-01-01T00:00:00Z',
            'heartbeat_at_utc': '2000-01-01T00:00:00Z',
            'ttl_seconds': 60,
        }
        self.lock_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        evaluation = self.SessionLockManager(self.lock_path, ttl_seconds=60).inspect_lock()
        self.assertEqual(evaluation.status, 'stale')

    def test_cross_host_lock_inside_ttl_is_treated_as_live(self) -> None:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            'lock_id': 'lock_remote',
            'session_id': 'sess_remote',
            'project_id': 'lock_demo',
            'pid': 1234,
            'host': 'REMOTE-HOST-01',
            'acquired_at_utc': '2099-01-01T00:00:00Z',
            'heartbeat_at_utc': '2099-01-01T00:00:00Z',
            'ttl_seconds': 60,
        }
        self.lock_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        evaluation = self.SessionLockManager(self.lock_path, ttl_seconds=60).inspect_lock()
        self.assertEqual(evaluation.status, 'live')

    def test_cross_host_lock_after_ttl_becomes_stale_safe_candidate(self) -> None:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            'lock_id': 'lock_remote_old',
            'session_id': 'sess_remote_old',
            'project_id': 'lock_demo',
            'pid': 1234,
            'host': 'REMOTE-HOST-02',
            'acquired_at_utc': '2000-01-01T00:00:00Z',
            'heartbeat_at_utc': '2000-01-01T00:00:00Z',
            'ttl_seconds': 60,
        }
        self.lock_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        evaluation = self.SessionLockManager(self.lock_path, ttl_seconds=60).inspect_lock()
        self.assertEqual(evaluation.status, 'stale_safe_candidate')


if __name__ == '__main__':
    import unittest

    unittest.main()
