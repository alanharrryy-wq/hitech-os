from __future__ import annotations

from tools.hos.git_sentinel_modular.sentinel_supervisor.supervisor import supervised_run

def test_supervised_run_writes_heartbeat(sandbox_runtime):
    payload = supervised_run(lambda: {"ok": True}, run_id="demo")
    assert payload["result"] == {"ok": True}
    assert "heartbeat.json" in payload["heartbeat_file"]
