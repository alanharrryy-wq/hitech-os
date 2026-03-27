from __future__ import annotations

from ..plugins.registry import get_registry, list_registered_plugins
from ..shared.status_payloads import CombinedHealthSummary
from .runtime import build_runtime_status
from .supervision import build_scheduler_status, build_supervisor_status

def build_combined_status() -> CombinedHealthSummary:
    runtime = build_runtime_status()
    supervisor = build_supervisor_status()
    scheduler = build_scheduler_status()
    plugin_results = get_registry().run_health_checks()
    overall = "ready"
    if supervisor.zombie_detected:
        overall = "attention"
    return CombinedHealthSummary(
        overall_status=overall,
        runtime=runtime,
        supervisor=supervisor,
        scheduler=scheduler,
        plugins=plugin_results or list_registered_plugins(),
    )
