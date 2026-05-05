"""Replay builder 012 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.012.01", "route", "route.replay.012.01", True),
        SwitchEntry("switch.replay.012.02", "boundary", "boundary.replay.012.02", True),
        SwitchEntry("switch.replay.012.03", "module", "module.replay.012.03", True),
        SwitchEntry("switch.replay.012.04", "route", "route.replay.012.04", True),
        SwitchEntry("switch.replay.012.05", "boundary", "boundary.replay.012.05", True),
        SwitchEntry("switch.replay.012.06", "module", "module.replay.012.06", True),
        SwitchEntry("switch.replay.012.07", "route", "route.replay.012.07", True),
        SwitchEntry("switch.replay.012.08", "boundary", "boundary.replay.012.08", True),
        SwitchEntry("switch.replay.012.09", "module", "module.replay.012.09", True),
        SwitchEntry("switch.replay.012.10", "route", "route.replay.012.10", True),
        SwitchEntry("switch.replay.012.11", "boundary", "boundary.replay.012.11", True),
        SwitchEntry("switch.replay.012.12", "module", "module.replay.012.12", True),
        SwitchEntry("switch.replay.012.13", "route", "route.replay.012.13", True),
        SwitchEntry("switch.replay.012.14", "boundary", "boundary.replay.012.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.012.01": False,
        "switch.replay.012.02": "bad",
        "route.replay.012.03": True,
        "switch.replay.012.04": False,
        "route.replay.012.05": "bad",
        "switch.replay.012.06": True,
        "route.replay.012.07": False,
        "switch.replay.012.08": "bad",
        "route.replay.012.09": True,
        "switch.replay.012.10": False,
        "route.replay.012.11": "bad",
        "switch.replay.012.12": True,
        "route.replay.012.13": False,
        "switch.replay.012.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_012",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
