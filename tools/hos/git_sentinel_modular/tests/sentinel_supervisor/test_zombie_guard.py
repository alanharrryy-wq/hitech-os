from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from tools.hos.git_sentinel_modular.sentinel_supervisor.zombie_guard import detect_zombie_state

def test_detect_zombie_state_flags_stale_heartbeat(tmp_path):
    heartbeat = tmp_path / "heartbeat.json"
    stale = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    heartbeat.write_text(json.dumps({"updated_at": stale}), encoding="utf-8")
    assert detect_zombie_state(heartbeat, max_staleness_seconds=60) is True
