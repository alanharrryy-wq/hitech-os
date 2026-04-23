"""Replay builder 018 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.018.01", "route", "route.replay.018.01", True),
        SwitchEntry("switch.replay.018.02", "boundary", "boundary.replay.018.02", True),
        SwitchEntry("switch.replay.018.03", "module", "module.replay.018.03", True),
        SwitchEntry("switch.replay.018.04", "route", "route.replay.018.04", True),
        SwitchEntry("switch.replay.018.05", "boundary", "boundary.replay.018.05", True),
        SwitchEntry("switch.replay.018.06", "module", "module.replay.018.06", True),
        SwitchEntry("switch.replay.018.07", "route", "route.replay.018.07", True),
        SwitchEntry("switch.replay.018.08", "boundary", "boundary.replay.018.08", True),
        SwitchEntry("switch.replay.018.09", "module", "module.replay.018.09", True),
        SwitchEntry("switch.replay.018.10", "route", "route.replay.018.10", True),
        SwitchEntry("switch.replay.018.11", "boundary", "boundary.replay.018.11", True),
        SwitchEntry("switch.replay.018.12", "module", "module.replay.018.12", True),
        SwitchEntry("switch.replay.018.13", "route", "route.replay.018.13", True),
        SwitchEntry("switch.replay.018.14", "boundary", "boundary.replay.018.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.018.01": False,
        "switch.replay.018.02": "bad",
        "route.replay.018.03": True,
        "switch.replay.018.04": False,
        "route.replay.018.05": "bad",
        "switch.replay.018.06": True,
        "route.replay.018.07": False,
        "switch.replay.018.08": "bad",
        "route.replay.018.09": True,
        "switch.replay.018.10": False,
        "route.replay.018.11": "bad",
        "switch.replay.018.12": True,
        "route.replay.018.13": False,
        "switch.replay.018.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_018",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
