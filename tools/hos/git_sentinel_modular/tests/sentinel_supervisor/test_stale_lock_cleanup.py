from __future__ import annotations

import os
import time

from tools.hos.git_sentinel_modular.sentinel_supervisor.stale_lock_cleanup import cleanup_stale_locks

def test_cleanup_stale_locks_removes_old_files(tmp_path):
    lock_dir = tmp_path / "locks"
    lock_dir.mkdir()
    old_lock = lock_dir / "old.lock"
    old_lock.write_text("x", encoding="utf-8")
    old_time = time.time() - 7200
    os.utime(old_lock, (old_time, old_time))

    cleaned = cleanup_stale_locks(lock_dir, max_age_seconds=60)
    assert cleaned == 1
    assert not old_lock.exists()
