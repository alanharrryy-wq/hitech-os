"""Replay builder 005 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.005.01", "route", "route.replay.005.01", False),
        SwitchEntry("switch.replay.005.02", "boundary", "boundary.replay.005.02", True),
        SwitchEntry("switch.replay.005.03", "module", "module.replay.005.03", False),
        SwitchEntry("switch.replay.005.04", "route", "route.replay.005.04", True),
        SwitchEntry("switch.replay.005.05", "boundary", "boundary.replay.005.05", False),
        SwitchEntry("switch.replay.005.06", "module", "module.replay.005.06", True),
        SwitchEntry("switch.replay.005.07", "route", "route.replay.005.07", False),
        SwitchEntry("switch.replay.005.08", "boundary", "boundary.replay.005.08", True),
        SwitchEntry("switch.replay.005.09", "module", "module.replay.005.09", False),
        SwitchEntry("switch.replay.005.10", "route", "route.replay.005.10", True),
        SwitchEntry("switch.replay.005.11", "boundary", "boundary.replay.005.11", False),
        SwitchEntry("switch.replay.005.12", "module", "module.replay.005.12", True),
        SwitchEntry("switch.replay.005.13", "route", "route.replay.005.13", False),
        SwitchEntry("switch.replay.005.14", "boundary", "boundary.replay.005.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.005.01": False,
        "switch.replay.005.02": "bad",
        "route.replay.005.03": True,
        "switch.replay.005.04": False,
        "route.replay.005.05": "bad",
        "switch.replay.005.06": True,
        "route.replay.005.07": False,
        "switch.replay.005.08": "bad",
        "route.replay.005.09": True,
        "switch.replay.005.10": False,
        "route.replay.005.11": "bad",
        "switch.replay.005.12": True,
        "route.replay.005.13": False,
        "switch.replay.005.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_005",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
