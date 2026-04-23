"""Replay builder 032 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.032.01", "route", "route.replay.032.01", True),
        SwitchEntry("switch.replay.032.02", "boundary", "boundary.replay.032.02", True),
        SwitchEntry("switch.replay.032.03", "module", "module.replay.032.03", True),
        SwitchEntry("switch.replay.032.04", "route", "route.replay.032.04", True),
        SwitchEntry("switch.replay.032.05", "boundary", "boundary.replay.032.05", True),
        SwitchEntry("switch.replay.032.06", "module", "module.replay.032.06", True),
        SwitchEntry("switch.replay.032.07", "route", "route.replay.032.07", True),
        SwitchEntry("switch.replay.032.08", "boundary", "boundary.replay.032.08", True),
        SwitchEntry("switch.replay.032.09", "module", "module.replay.032.09", True),
        SwitchEntry("switch.replay.032.10", "route", "route.replay.032.10", True),
        SwitchEntry("switch.replay.032.11", "boundary", "boundary.replay.032.11", True),
        SwitchEntry("switch.replay.032.12", "module", "module.replay.032.12", True),
        SwitchEntry("switch.replay.032.13", "route", "route.replay.032.13", True),
        SwitchEntry("switch.replay.032.14", "boundary", "boundary.replay.032.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.032.01": False,
        "switch.replay.032.02": "bad",
        "route.replay.032.03": True,
        "switch.replay.032.04": False,
        "route.replay.032.05": "bad",
        "switch.replay.032.06": True,
        "route.replay.032.07": False,
        "switch.replay.032.08": "bad",
        "route.replay.032.09": True,
        "switch.replay.032.10": False,
        "route.replay.032.11": "bad",
        "switch.replay.032.12": True,
        "route.replay.032.13": False,
        "switch.replay.032.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_032",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
