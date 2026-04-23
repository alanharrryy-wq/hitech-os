"""Replay builder 011 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.011.01", "route", "route.replay.011.01", False),
        SwitchEntry("switch.replay.011.02", "boundary", "boundary.replay.011.02", True),
        SwitchEntry("switch.replay.011.03", "module", "module.replay.011.03", False),
        SwitchEntry("switch.replay.011.04", "route", "route.replay.011.04", True),
        SwitchEntry("switch.replay.011.05", "boundary", "boundary.replay.011.05", False),
        SwitchEntry("switch.replay.011.06", "module", "module.replay.011.06", True),
        SwitchEntry("switch.replay.011.07", "route", "route.replay.011.07", False),
        SwitchEntry("switch.replay.011.08", "boundary", "boundary.replay.011.08", True),
        SwitchEntry("switch.replay.011.09", "module", "module.replay.011.09", False),
        SwitchEntry("switch.replay.011.10", "route", "route.replay.011.10", True),
        SwitchEntry("switch.replay.011.11", "boundary", "boundary.replay.011.11", False),
        SwitchEntry("switch.replay.011.12", "module", "module.replay.011.12", True),
        SwitchEntry("switch.replay.011.13", "route", "route.replay.011.13", False),
        SwitchEntry("switch.replay.011.14", "boundary", "boundary.replay.011.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.011.01": False,
        "switch.replay.011.02": "bad",
        "route.replay.011.03": True,
        "switch.replay.011.04": False,
        "route.replay.011.05": "bad",
        "switch.replay.011.06": True,
        "route.replay.011.07": False,
        "switch.replay.011.08": "bad",
        "route.replay.011.09": True,
        "switch.replay.011.10": False,
        "route.replay.011.11": "bad",
        "switch.replay.011.12": True,
        "route.replay.011.13": False,
        "switch.replay.011.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_011",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
