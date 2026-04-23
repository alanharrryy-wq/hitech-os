"""Replay builder 040 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.040.01", "route", "route.replay.040.01", True),
        SwitchEntry("switch.replay.040.02", "boundary", "boundary.replay.040.02", True),
        SwitchEntry("switch.replay.040.03", "module", "module.replay.040.03", True),
        SwitchEntry("switch.replay.040.04", "route", "route.replay.040.04", True),
        SwitchEntry("switch.replay.040.05", "boundary", "boundary.replay.040.05", True),
        SwitchEntry("switch.replay.040.06", "module", "module.replay.040.06", True),
        SwitchEntry("switch.replay.040.07", "route", "route.replay.040.07", True),
        SwitchEntry("switch.replay.040.08", "boundary", "boundary.replay.040.08", True),
        SwitchEntry("switch.replay.040.09", "module", "module.replay.040.09", True),
        SwitchEntry("switch.replay.040.10", "route", "route.replay.040.10", True),
        SwitchEntry("switch.replay.040.11", "boundary", "boundary.replay.040.11", True),
        SwitchEntry("switch.replay.040.12", "module", "module.replay.040.12", True),
        SwitchEntry("switch.replay.040.13", "route", "route.replay.040.13", True),
        SwitchEntry("switch.replay.040.14", "boundary", "boundary.replay.040.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.040.01": False,
        "switch.replay.040.02": "bad",
        "route.replay.040.03": True,
        "switch.replay.040.04": False,
        "route.replay.040.05": "bad",
        "switch.replay.040.06": True,
        "route.replay.040.07": False,
        "switch.replay.040.08": "bad",
        "route.replay.040.09": True,
        "switch.replay.040.10": False,
        "route.replay.040.11": "bad",
        "switch.replay.040.12": True,
        "route.replay.040.13": False,
        "switch.replay.040.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_040",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
