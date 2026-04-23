"""Replay builder 014 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.014.01", "route", "route.replay.014.01", True),
        SwitchEntry("switch.replay.014.02", "boundary", "boundary.replay.014.02", True),
        SwitchEntry("switch.replay.014.03", "module", "module.replay.014.03", True),
        SwitchEntry("switch.replay.014.04", "route", "route.replay.014.04", True),
        SwitchEntry("switch.replay.014.05", "boundary", "boundary.replay.014.05", True),
        SwitchEntry("switch.replay.014.06", "module", "module.replay.014.06", True),
        SwitchEntry("switch.replay.014.07", "route", "route.replay.014.07", True),
        SwitchEntry("switch.replay.014.08", "boundary", "boundary.replay.014.08", True),
        SwitchEntry("switch.replay.014.09", "module", "module.replay.014.09", True),
        SwitchEntry("switch.replay.014.10", "route", "route.replay.014.10", True),
        SwitchEntry("switch.replay.014.11", "boundary", "boundary.replay.014.11", True),
        SwitchEntry("switch.replay.014.12", "module", "module.replay.014.12", True),
        SwitchEntry("switch.replay.014.13", "route", "route.replay.014.13", True),
        SwitchEntry("switch.replay.014.14", "boundary", "boundary.replay.014.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.014.01": False,
        "switch.replay.014.02": "bad",
        "route.replay.014.03": True,
        "switch.replay.014.04": False,
        "route.replay.014.05": "bad",
        "switch.replay.014.06": True,
        "route.replay.014.07": False,
        "switch.replay.014.08": "bad",
        "route.replay.014.09": True,
        "switch.replay.014.10": False,
        "route.replay.014.11": "bad",
        "switch.replay.014.12": True,
        "route.replay.014.13": False,
        "switch.replay.014.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_014",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
