"""Replay builder 035 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.035.01", "route", "route.replay.035.01", False),
        SwitchEntry("switch.replay.035.02", "boundary", "boundary.replay.035.02", True),
        SwitchEntry("switch.replay.035.03", "module", "module.replay.035.03", False),
        SwitchEntry("switch.replay.035.04", "route", "route.replay.035.04", True),
        SwitchEntry("switch.replay.035.05", "boundary", "boundary.replay.035.05", False),
        SwitchEntry("switch.replay.035.06", "module", "module.replay.035.06", True),
        SwitchEntry("switch.replay.035.07", "route", "route.replay.035.07", False),
        SwitchEntry("switch.replay.035.08", "boundary", "boundary.replay.035.08", True),
        SwitchEntry("switch.replay.035.09", "module", "module.replay.035.09", False),
        SwitchEntry("switch.replay.035.10", "route", "route.replay.035.10", True),
        SwitchEntry("switch.replay.035.11", "boundary", "boundary.replay.035.11", False),
        SwitchEntry("switch.replay.035.12", "module", "module.replay.035.12", True),
        SwitchEntry("switch.replay.035.13", "route", "route.replay.035.13", False),
        SwitchEntry("switch.replay.035.14", "boundary", "boundary.replay.035.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.035.01": False,
        "switch.replay.035.02": "bad",
        "route.replay.035.03": True,
        "switch.replay.035.04": False,
        "route.replay.035.05": "bad",
        "switch.replay.035.06": True,
        "route.replay.035.07": False,
        "switch.replay.035.08": "bad",
        "route.replay.035.09": True,
        "switch.replay.035.10": False,
        "route.replay.035.11": "bad",
        "switch.replay.035.12": True,
        "route.replay.035.13": False,
        "switch.replay.035.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_035",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
