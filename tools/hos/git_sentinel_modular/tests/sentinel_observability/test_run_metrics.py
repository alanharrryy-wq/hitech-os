from __future__ import annotations

from tools.hos.git_sentinel_modular.sentinel_observability.run_metrics import RunMetrics

def test_run_metrics_collects_counters(tmp_path):
    metrics = RunMetrics(run_id="demo")
    metrics.increment("planned")
    metrics.increment("planned", 2)
    path = metrics.write(tmp_path / "metrics.json")
    assert metrics.counters["planned"] == 3
    assert path.exists()
