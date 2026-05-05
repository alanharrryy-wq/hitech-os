"""Replay builder 017 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.017.01", "route", "route.replay.017.01", False),
        SwitchEntry("switch.replay.017.02", "boundary", "boundary.replay.017.02", True),
        SwitchEntry("switch.replay.017.03", "module", "module.replay.017.03", False),
        SwitchEntry("switch.replay.017.04", "route", "route.replay.017.04", True),
        SwitchEntry("switch.replay.017.05", "boundary", "boundary.replay.017.05", False),
        SwitchEntry("switch.replay.017.06", "module", "module.replay.017.06", True),
        SwitchEntry("switch.replay.017.07", "route", "route.replay.017.07", False),
        SwitchEntry("switch.replay.017.08", "boundary", "boundary.replay.017.08", True),
        SwitchEntry("switch.replay.017.09", "module", "module.replay.017.09", False),
        SwitchEntry("switch.replay.017.10", "route", "route.replay.017.10", True),
        SwitchEntry("switch.replay.017.11", "boundary", "boundary.replay.017.11", False),
        SwitchEntry("switch.replay.017.12", "module", "module.replay.017.12", True),
        SwitchEntry("switch.replay.017.13", "route", "route.replay.017.13", False),
        SwitchEntry("switch.replay.017.14", "boundary", "boundary.replay.017.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.017.01": False,
        "switch.replay.017.02": "bad",
        "route.replay.017.03": True,
        "switch.replay.017.04": False,
        "route.replay.017.05": "bad",
        "switch.replay.017.06": True,
        "route.replay.017.07": False,
        "switch.replay.017.08": "bad",
        "route.replay.017.09": True,
        "switch.replay.017.10": False,
        "route.replay.017.11": "bad",
        "switch.replay.017.12": True,
        "route.replay.017.13": False,
        "switch.replay.017.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_017",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
