"""Replay builder 006 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.006.01", "route", "route.replay.006.01", True),
        SwitchEntry("switch.replay.006.02", "boundary", "boundary.replay.006.02", True),
        SwitchEntry("switch.replay.006.03", "module", "module.replay.006.03", True),
        SwitchEntry("switch.replay.006.04", "route", "route.replay.006.04", True),
        SwitchEntry("switch.replay.006.05", "boundary", "boundary.replay.006.05", True),
        SwitchEntry("switch.replay.006.06", "module", "module.replay.006.06", True),
        SwitchEntry("switch.replay.006.07", "route", "route.replay.006.07", True),
        SwitchEntry("switch.replay.006.08", "boundary", "boundary.replay.006.08", True),
        SwitchEntry("switch.replay.006.09", "module", "module.replay.006.09", True),
        SwitchEntry("switch.replay.006.10", "route", "route.replay.006.10", True),
        SwitchEntry("switch.replay.006.11", "boundary", "boundary.replay.006.11", True),
        SwitchEntry("switch.replay.006.12", "module", "module.replay.006.12", True),
        SwitchEntry("switch.replay.006.13", "route", "route.replay.006.13", True),
        SwitchEntry("switch.replay.006.14", "boundary", "boundary.replay.006.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.006.01": False,
        "switch.replay.006.02": "bad",
        "route.replay.006.03": True,
        "switch.replay.006.04": False,
        "route.replay.006.05": "bad",
        "switch.replay.006.06": True,
        "route.replay.006.07": False,
        "switch.replay.006.08": "bad",
        "route.replay.006.09": True,
        "switch.replay.006.10": False,
        "route.replay.006.11": "bad",
        "switch.replay.006.12": True,
        "route.replay.006.13": False,
        "switch.replay.006.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_006",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
