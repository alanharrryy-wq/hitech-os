"""Replay builder 015 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.015.01", "route", "route.replay.015.01", False),
        SwitchEntry("switch.replay.015.02", "boundary", "boundary.replay.015.02", True),
        SwitchEntry("switch.replay.015.03", "module", "module.replay.015.03", False),
        SwitchEntry("switch.replay.015.04", "route", "route.replay.015.04", True),
        SwitchEntry("switch.replay.015.05", "boundary", "boundary.replay.015.05", False),
        SwitchEntry("switch.replay.015.06", "module", "module.replay.015.06", True),
        SwitchEntry("switch.replay.015.07", "route", "route.replay.015.07", False),
        SwitchEntry("switch.replay.015.08", "boundary", "boundary.replay.015.08", True),
        SwitchEntry("switch.replay.015.09", "module", "module.replay.015.09", False),
        SwitchEntry("switch.replay.015.10", "route", "route.replay.015.10", True),
        SwitchEntry("switch.replay.015.11", "boundary", "boundary.replay.015.11", False),
        SwitchEntry("switch.replay.015.12", "module", "module.replay.015.12", True),
        SwitchEntry("switch.replay.015.13", "route", "route.replay.015.13", False),
        SwitchEntry("switch.replay.015.14", "boundary", "boundary.replay.015.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.015.01": False,
        "switch.replay.015.02": "bad",
        "route.replay.015.03": True,
        "switch.replay.015.04": False,
        "route.replay.015.05": "bad",
        "switch.replay.015.06": True,
        "route.replay.015.07": False,
        "switch.replay.015.08": "bad",
        "route.replay.015.09": True,
        "switch.replay.015.10": False,
        "route.replay.015.11": "bad",
        "switch.replay.015.12": True,
        "route.replay.015.13": False,
        "switch.replay.015.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_015",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
