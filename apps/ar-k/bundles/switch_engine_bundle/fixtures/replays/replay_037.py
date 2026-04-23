"""Replay builder 037 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.037.01", "route", "route.replay.037.01", False),
        SwitchEntry("switch.replay.037.02", "boundary", "boundary.replay.037.02", True),
        SwitchEntry("switch.replay.037.03", "module", "module.replay.037.03", False),
        SwitchEntry("switch.replay.037.04", "route", "route.replay.037.04", True),
        SwitchEntry("switch.replay.037.05", "boundary", "boundary.replay.037.05", False),
        SwitchEntry("switch.replay.037.06", "module", "module.replay.037.06", True),
        SwitchEntry("switch.replay.037.07", "route", "route.replay.037.07", False),
        SwitchEntry("switch.replay.037.08", "boundary", "boundary.replay.037.08", True),
        SwitchEntry("switch.replay.037.09", "module", "module.replay.037.09", False),
        SwitchEntry("switch.replay.037.10", "route", "route.replay.037.10", True),
        SwitchEntry("switch.replay.037.11", "boundary", "boundary.replay.037.11", False),
        SwitchEntry("switch.replay.037.12", "module", "module.replay.037.12", True),
        SwitchEntry("switch.replay.037.13", "route", "route.replay.037.13", False),
        SwitchEntry("switch.replay.037.14", "boundary", "boundary.replay.037.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.037.01": False,
        "switch.replay.037.02": "bad",
        "route.replay.037.03": True,
        "switch.replay.037.04": False,
        "route.replay.037.05": "bad",
        "switch.replay.037.06": True,
        "route.replay.037.07": False,
        "switch.replay.037.08": "bad",
        "route.replay.037.09": True,
        "switch.replay.037.10": False,
        "route.replay.037.11": "bad",
        "switch.replay.037.12": True,
        "route.replay.037.13": False,
        "switch.replay.037.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_037",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
