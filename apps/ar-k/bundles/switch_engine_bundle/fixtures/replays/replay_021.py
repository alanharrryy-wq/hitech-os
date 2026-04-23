"""Replay builder 021 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.021.01", "route", "route.replay.021.01", False),
        SwitchEntry("switch.replay.021.02", "boundary", "boundary.replay.021.02", True),
        SwitchEntry("switch.replay.021.03", "module", "module.replay.021.03", False),
        SwitchEntry("switch.replay.021.04", "route", "route.replay.021.04", True),
        SwitchEntry("switch.replay.021.05", "boundary", "boundary.replay.021.05", False),
        SwitchEntry("switch.replay.021.06", "module", "module.replay.021.06", True),
        SwitchEntry("switch.replay.021.07", "route", "route.replay.021.07", False),
        SwitchEntry("switch.replay.021.08", "boundary", "boundary.replay.021.08", True),
        SwitchEntry("switch.replay.021.09", "module", "module.replay.021.09", False),
        SwitchEntry("switch.replay.021.10", "route", "route.replay.021.10", True),
        SwitchEntry("switch.replay.021.11", "boundary", "boundary.replay.021.11", False),
        SwitchEntry("switch.replay.021.12", "module", "module.replay.021.12", True),
        SwitchEntry("switch.replay.021.13", "route", "route.replay.021.13", False),
        SwitchEntry("switch.replay.021.14", "boundary", "boundary.replay.021.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.021.01": False,
        "switch.replay.021.02": "bad",
        "route.replay.021.03": True,
        "switch.replay.021.04": False,
        "route.replay.021.05": "bad",
        "switch.replay.021.06": True,
        "route.replay.021.07": False,
        "switch.replay.021.08": "bad",
        "route.replay.021.09": True,
        "switch.replay.021.10": False,
        "route.replay.021.11": "bad",
        "switch.replay.021.12": True,
        "route.replay.021.13": False,
        "switch.replay.021.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_021",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
