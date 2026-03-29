"""Scenario catalog for deterministic data simulator."""

from .degraded import SCENARIO as DEGRADED_SCENARIO
from .incident import SCENARIO as INCIDENT_SCENARIO
from .normal import SCENARIO as NORMAL_SCENARIO
from .recovery import SCENARIO as RECOVERY_SCENARIO
from .spike import SCENARIO as SPIKE_SCENARIO

SCENARIOS = {
    "degraded": DEGRADED_SCENARIO,
    "incident": INCIDENT_SCENARIO,
    "normal": NORMAL_SCENARIO,
    "recovery": RECOVERY_SCENARIO,
    "spike": SPIKE_SCENARIO,
}

