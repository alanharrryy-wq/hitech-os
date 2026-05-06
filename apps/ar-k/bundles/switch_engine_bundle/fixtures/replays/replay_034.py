"""Replay builder 034 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.034.01", "route", "route.replay.034.01", True),
        SwitchEntry("switch.replay.034.02", "boundary", "boundary.replay.034.02", True),
        SwitchEntry("switch.replay.034.03", "module", "module.replay.034.03", True),
        SwitchEntry("switch.replay.034.04", "route", "route.replay.034.04", True),
        SwitchEntry("switch.replay.034.05", "boundary", "boundary.replay.034.05", True),
        SwitchEntry("switch.replay.034.06", "module", "module.replay.034.06", True),
        SwitchEntry("switch.replay.034.07", "route", "route.replay.034.07", True),
        SwitchEntry("switch.replay.034.08", "boundary", "boundary.replay.034.08", True),
        SwitchEntry("switch.replay.034.09", "module", "module.replay.034.09", True),
        SwitchEntry("switch.replay.034.10", "route", "route.replay.034.10", True),
        SwitchEntry("switch.replay.034.11", "boundary", "boundary.replay.034.11", True),
        SwitchEntry("switch.replay.034.12", "module", "module.replay.034.12", True),
        SwitchEntry("switch.replay.034.13", "route", "route.replay.034.13", True),
        SwitchEntry("switch.replay.034.14", "boundary", "boundary.replay.034.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.034.01": False,
        "switch.replay.034.02": "bad",
        "route.replay.034.03": True,
        "switch.replay.034.04": False,
        "route.replay.034.05": "bad",
        "switch.replay.034.06": True,
        "route.replay.034.07": False,
        "switch.replay.034.08": "bad",
        "route.replay.034.09": True,
        "switch.replay.034.10": False,
        "route.replay.034.11": "bad",
        "switch.replay.034.12": True,
        "route.replay.034.13": False,
        "switch.replay.034.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_034",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
