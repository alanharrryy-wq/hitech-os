"""Replay builder 008 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.008.01", "route", "route.replay.008.01", True),
        SwitchEntry("switch.replay.008.02", "boundary", "boundary.replay.008.02", True),
        SwitchEntry("switch.replay.008.03", "module", "module.replay.008.03", True),
        SwitchEntry("switch.replay.008.04", "route", "route.replay.008.04", True),
        SwitchEntry("switch.replay.008.05", "boundary", "boundary.replay.008.05", True),
        SwitchEntry("switch.replay.008.06", "module", "module.replay.008.06", True),
        SwitchEntry("switch.replay.008.07", "route", "route.replay.008.07", True),
        SwitchEntry("switch.replay.008.08", "boundary", "boundary.replay.008.08", True),
        SwitchEntry("switch.replay.008.09", "module", "module.replay.008.09", True),
        SwitchEntry("switch.replay.008.10", "route", "route.replay.008.10", True),
        SwitchEntry("switch.replay.008.11", "boundary", "boundary.replay.008.11", True),
        SwitchEntry("switch.replay.008.12", "module", "module.replay.008.12", True),
        SwitchEntry("switch.replay.008.13", "route", "route.replay.008.13", True),
        SwitchEntry("switch.replay.008.14", "boundary", "boundary.replay.008.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.008.01": False,
        "switch.replay.008.02": "bad",
        "route.replay.008.03": True,
        "switch.replay.008.04": False,
        "route.replay.008.05": "bad",
        "switch.replay.008.06": True,
        "route.replay.008.07": False,
        "switch.replay.008.08": "bad",
        "route.replay.008.09": True,
        "switch.replay.008.10": False,
        "route.replay.008.11": "bad",
        "switch.replay.008.12": True,
        "route.replay.008.13": False,
        "switch.replay.008.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_008",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
