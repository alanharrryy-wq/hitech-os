"""Replay builder 025 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.025.01", "route", "route.replay.025.01", False),
        SwitchEntry("switch.replay.025.02", "boundary", "boundary.replay.025.02", True),
        SwitchEntry("switch.replay.025.03", "module", "module.replay.025.03", False),
        SwitchEntry("switch.replay.025.04", "route", "route.replay.025.04", True),
        SwitchEntry("switch.replay.025.05", "boundary", "boundary.replay.025.05", False),
        SwitchEntry("switch.replay.025.06", "module", "module.replay.025.06", True),
        SwitchEntry("switch.replay.025.07", "route", "route.replay.025.07", False),
        SwitchEntry("switch.replay.025.08", "boundary", "boundary.replay.025.08", True),
        SwitchEntry("switch.replay.025.09", "module", "module.replay.025.09", False),
        SwitchEntry("switch.replay.025.10", "route", "route.replay.025.10", True),
        SwitchEntry("switch.replay.025.11", "boundary", "boundary.replay.025.11", False),
        SwitchEntry("switch.replay.025.12", "module", "module.replay.025.12", True),
        SwitchEntry("switch.replay.025.13", "route", "route.replay.025.13", False),
        SwitchEntry("switch.replay.025.14", "boundary", "boundary.replay.025.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.025.01": False,
        "switch.replay.025.02": "bad",
        "route.replay.025.03": True,
        "switch.replay.025.04": False,
        "route.replay.025.05": "bad",
        "switch.replay.025.06": True,
        "route.replay.025.07": False,
        "switch.replay.025.08": "bad",
        "route.replay.025.09": True,
        "switch.replay.025.10": False,
        "route.replay.025.11": "bad",
        "switch.replay.025.12": True,
        "route.replay.025.13": False,
        "switch.replay.025.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_025",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
