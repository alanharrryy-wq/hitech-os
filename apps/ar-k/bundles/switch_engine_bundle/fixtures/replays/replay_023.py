"""Replay builder 023 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.023.01", "route", "route.replay.023.01", False),
        SwitchEntry("switch.replay.023.02", "boundary", "boundary.replay.023.02", True),
        SwitchEntry("switch.replay.023.03", "module", "module.replay.023.03", False),
        SwitchEntry("switch.replay.023.04", "route", "route.replay.023.04", True),
        SwitchEntry("switch.replay.023.05", "boundary", "boundary.replay.023.05", False),
        SwitchEntry("switch.replay.023.06", "module", "module.replay.023.06", True),
        SwitchEntry("switch.replay.023.07", "route", "route.replay.023.07", False),
        SwitchEntry("switch.replay.023.08", "boundary", "boundary.replay.023.08", True),
        SwitchEntry("switch.replay.023.09", "module", "module.replay.023.09", False),
        SwitchEntry("switch.replay.023.10", "route", "route.replay.023.10", True),
        SwitchEntry("switch.replay.023.11", "boundary", "boundary.replay.023.11", False),
        SwitchEntry("switch.replay.023.12", "module", "module.replay.023.12", True),
        SwitchEntry("switch.replay.023.13", "route", "route.replay.023.13", False),
        SwitchEntry("switch.replay.023.14", "boundary", "boundary.replay.023.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.023.01": False,
        "switch.replay.023.02": "bad",
        "route.replay.023.03": True,
        "switch.replay.023.04": False,
        "route.replay.023.05": "bad",
        "switch.replay.023.06": True,
        "route.replay.023.07": False,
        "switch.replay.023.08": "bad",
        "route.replay.023.09": True,
        "switch.replay.023.10": False,
        "route.replay.023.11": "bad",
        "switch.replay.023.12": True,
        "route.replay.023.13": False,
        "switch.replay.023.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_023",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
