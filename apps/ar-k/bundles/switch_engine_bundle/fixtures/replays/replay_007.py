"""Replay builder 007 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.007.01", "route", "route.replay.007.01", False),
        SwitchEntry("switch.replay.007.02", "boundary", "boundary.replay.007.02", True),
        SwitchEntry("switch.replay.007.03", "module", "module.replay.007.03", False),
        SwitchEntry("switch.replay.007.04", "route", "route.replay.007.04", True),
        SwitchEntry("switch.replay.007.05", "boundary", "boundary.replay.007.05", False),
        SwitchEntry("switch.replay.007.06", "module", "module.replay.007.06", True),
        SwitchEntry("switch.replay.007.07", "route", "route.replay.007.07", False),
        SwitchEntry("switch.replay.007.08", "boundary", "boundary.replay.007.08", True),
        SwitchEntry("switch.replay.007.09", "module", "module.replay.007.09", False),
        SwitchEntry("switch.replay.007.10", "route", "route.replay.007.10", True),
        SwitchEntry("switch.replay.007.11", "boundary", "boundary.replay.007.11", False),
        SwitchEntry("switch.replay.007.12", "module", "module.replay.007.12", True),
        SwitchEntry("switch.replay.007.13", "route", "route.replay.007.13", False),
        SwitchEntry("switch.replay.007.14", "boundary", "boundary.replay.007.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.007.01": False,
        "switch.replay.007.02": "bad",
        "route.replay.007.03": True,
        "switch.replay.007.04": False,
        "route.replay.007.05": "bad",
        "switch.replay.007.06": True,
        "route.replay.007.07": False,
        "switch.replay.007.08": "bad",
        "route.replay.007.09": True,
        "switch.replay.007.10": False,
        "route.replay.007.11": "bad",
        "switch.replay.007.12": True,
        "route.replay.007.13": False,
        "switch.replay.007.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_007",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
