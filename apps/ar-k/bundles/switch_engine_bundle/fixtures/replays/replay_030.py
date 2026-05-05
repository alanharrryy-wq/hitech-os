"""Replay builder 030 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.030.01", "route", "route.replay.030.01", True),
        SwitchEntry("switch.replay.030.02", "boundary", "boundary.replay.030.02", True),
        SwitchEntry("switch.replay.030.03", "module", "module.replay.030.03", True),
        SwitchEntry("switch.replay.030.04", "route", "route.replay.030.04", True),
        SwitchEntry("switch.replay.030.05", "boundary", "boundary.replay.030.05", True),
        SwitchEntry("switch.replay.030.06", "module", "module.replay.030.06", True),
        SwitchEntry("switch.replay.030.07", "route", "route.replay.030.07", True),
        SwitchEntry("switch.replay.030.08", "boundary", "boundary.replay.030.08", True),
        SwitchEntry("switch.replay.030.09", "module", "module.replay.030.09", True),
        SwitchEntry("switch.replay.030.10", "route", "route.replay.030.10", True),
        SwitchEntry("switch.replay.030.11", "boundary", "boundary.replay.030.11", True),
        SwitchEntry("switch.replay.030.12", "module", "module.replay.030.12", True),
        SwitchEntry("switch.replay.030.13", "route", "route.replay.030.13", True),
        SwitchEntry("switch.replay.030.14", "boundary", "boundary.replay.030.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.030.01": False,
        "switch.replay.030.02": "bad",
        "route.replay.030.03": True,
        "switch.replay.030.04": False,
        "route.replay.030.05": "bad",
        "switch.replay.030.06": True,
        "route.replay.030.07": False,
        "switch.replay.030.08": "bad",
        "route.replay.030.09": True,
        "switch.replay.030.10": False,
        "route.replay.030.11": "bad",
        "switch.replay.030.12": True,
        "route.replay.030.13": False,
        "switch.replay.030.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_030",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
