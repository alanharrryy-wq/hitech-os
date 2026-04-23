"""Replay builder 033 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.033.01", "route", "route.replay.033.01", False),
        SwitchEntry("switch.replay.033.02", "boundary", "boundary.replay.033.02", True),
        SwitchEntry("switch.replay.033.03", "module", "module.replay.033.03", False),
        SwitchEntry("switch.replay.033.04", "route", "route.replay.033.04", True),
        SwitchEntry("switch.replay.033.05", "boundary", "boundary.replay.033.05", False),
        SwitchEntry("switch.replay.033.06", "module", "module.replay.033.06", True),
        SwitchEntry("switch.replay.033.07", "route", "route.replay.033.07", False),
        SwitchEntry("switch.replay.033.08", "boundary", "boundary.replay.033.08", True),
        SwitchEntry("switch.replay.033.09", "module", "module.replay.033.09", False),
        SwitchEntry("switch.replay.033.10", "route", "route.replay.033.10", True),
        SwitchEntry("switch.replay.033.11", "boundary", "boundary.replay.033.11", False),
        SwitchEntry("switch.replay.033.12", "module", "module.replay.033.12", True),
        SwitchEntry("switch.replay.033.13", "route", "route.replay.033.13", False),
        SwitchEntry("switch.replay.033.14", "boundary", "boundary.replay.033.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.033.01": False,
        "switch.replay.033.02": "bad",
        "route.replay.033.03": True,
        "switch.replay.033.04": False,
        "route.replay.033.05": "bad",
        "switch.replay.033.06": True,
        "route.replay.033.07": False,
        "switch.replay.033.08": "bad",
        "route.replay.033.09": True,
        "switch.replay.033.10": False,
        "route.replay.033.11": "bad",
        "switch.replay.033.12": True,
        "route.replay.033.13": False,
        "switch.replay.033.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_033",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
