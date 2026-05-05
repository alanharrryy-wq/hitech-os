"""Replay builder 003 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.003.01", "route", "route.replay.003.01", False),
        SwitchEntry("switch.replay.003.02", "boundary", "boundary.replay.003.02", True),
        SwitchEntry("switch.replay.003.03", "module", "module.replay.003.03", False),
        SwitchEntry("switch.replay.003.04", "route", "route.replay.003.04", True),
        SwitchEntry("switch.replay.003.05", "boundary", "boundary.replay.003.05", False),
        SwitchEntry("switch.replay.003.06", "module", "module.replay.003.06", True),
        SwitchEntry("switch.replay.003.07", "route", "route.replay.003.07", False),
        SwitchEntry("switch.replay.003.08", "boundary", "boundary.replay.003.08", True),
        SwitchEntry("switch.replay.003.09", "module", "module.replay.003.09", False),
        SwitchEntry("switch.replay.003.10", "route", "route.replay.003.10", True),
        SwitchEntry("switch.replay.003.11", "boundary", "boundary.replay.003.11", False),
        SwitchEntry("switch.replay.003.12", "module", "module.replay.003.12", True),
        SwitchEntry("switch.replay.003.13", "route", "route.replay.003.13", False),
        SwitchEntry("switch.replay.003.14", "boundary", "boundary.replay.003.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.003.01": False,
        "switch.replay.003.02": "bad",
        "route.replay.003.03": True,
        "switch.replay.003.04": False,
        "route.replay.003.05": "bad",
        "switch.replay.003.06": True,
        "route.replay.003.07": False,
        "switch.replay.003.08": "bad",
        "route.replay.003.09": True,
        "switch.replay.003.10": False,
        "route.replay.003.11": "bad",
        "switch.replay.003.12": True,
        "route.replay.003.13": False,
        "switch.replay.003.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_003",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
