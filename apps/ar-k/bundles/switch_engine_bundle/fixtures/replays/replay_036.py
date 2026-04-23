"""Replay builder 036 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.036.01", "route", "route.replay.036.01", True),
        SwitchEntry("switch.replay.036.02", "boundary", "boundary.replay.036.02", True),
        SwitchEntry("switch.replay.036.03", "module", "module.replay.036.03", True),
        SwitchEntry("switch.replay.036.04", "route", "route.replay.036.04", True),
        SwitchEntry("switch.replay.036.05", "boundary", "boundary.replay.036.05", True),
        SwitchEntry("switch.replay.036.06", "module", "module.replay.036.06", True),
        SwitchEntry("switch.replay.036.07", "route", "route.replay.036.07", True),
        SwitchEntry("switch.replay.036.08", "boundary", "boundary.replay.036.08", True),
        SwitchEntry("switch.replay.036.09", "module", "module.replay.036.09", True),
        SwitchEntry("switch.replay.036.10", "route", "route.replay.036.10", True),
        SwitchEntry("switch.replay.036.11", "boundary", "boundary.replay.036.11", True),
        SwitchEntry("switch.replay.036.12", "module", "module.replay.036.12", True),
        SwitchEntry("switch.replay.036.13", "route", "route.replay.036.13", True),
        SwitchEntry("switch.replay.036.14", "boundary", "boundary.replay.036.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.036.01": False,
        "switch.replay.036.02": "bad",
        "route.replay.036.03": True,
        "switch.replay.036.04": False,
        "route.replay.036.05": "bad",
        "switch.replay.036.06": True,
        "route.replay.036.07": False,
        "switch.replay.036.08": "bad",
        "route.replay.036.09": True,
        "switch.replay.036.10": False,
        "route.replay.036.11": "bad",
        "switch.replay.036.12": True,
        "route.replay.036.13": False,
        "switch.replay.036.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_036",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
