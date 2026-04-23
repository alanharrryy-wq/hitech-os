"""Replay builder 027 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.027.01", "route", "route.replay.027.01", False),
        SwitchEntry("switch.replay.027.02", "boundary", "boundary.replay.027.02", True),
        SwitchEntry("switch.replay.027.03", "module", "module.replay.027.03", False),
        SwitchEntry("switch.replay.027.04", "route", "route.replay.027.04", True),
        SwitchEntry("switch.replay.027.05", "boundary", "boundary.replay.027.05", False),
        SwitchEntry("switch.replay.027.06", "module", "module.replay.027.06", True),
        SwitchEntry("switch.replay.027.07", "route", "route.replay.027.07", False),
        SwitchEntry("switch.replay.027.08", "boundary", "boundary.replay.027.08", True),
        SwitchEntry("switch.replay.027.09", "module", "module.replay.027.09", False),
        SwitchEntry("switch.replay.027.10", "route", "route.replay.027.10", True),
        SwitchEntry("switch.replay.027.11", "boundary", "boundary.replay.027.11", False),
        SwitchEntry("switch.replay.027.12", "module", "module.replay.027.12", True),
        SwitchEntry("switch.replay.027.13", "route", "route.replay.027.13", False),
        SwitchEntry("switch.replay.027.14", "boundary", "boundary.replay.027.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.027.01": False,
        "switch.replay.027.02": "bad",
        "route.replay.027.03": True,
        "switch.replay.027.04": False,
        "route.replay.027.05": "bad",
        "switch.replay.027.06": True,
        "route.replay.027.07": False,
        "switch.replay.027.08": "bad",
        "route.replay.027.09": True,
        "switch.replay.027.10": False,
        "route.replay.027.11": "bad",
        "switch.replay.027.12": True,
        "route.replay.027.13": False,
        "switch.replay.027.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_027",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
