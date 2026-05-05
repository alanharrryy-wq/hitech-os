"""Replay builder 020 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.020.01", "route", "route.replay.020.01", True),
        SwitchEntry("switch.replay.020.02", "boundary", "boundary.replay.020.02", True),
        SwitchEntry("switch.replay.020.03", "module", "module.replay.020.03", True),
        SwitchEntry("switch.replay.020.04", "route", "route.replay.020.04", True),
        SwitchEntry("switch.replay.020.05", "boundary", "boundary.replay.020.05", True),
        SwitchEntry("switch.replay.020.06", "module", "module.replay.020.06", True),
        SwitchEntry("switch.replay.020.07", "route", "route.replay.020.07", True),
        SwitchEntry("switch.replay.020.08", "boundary", "boundary.replay.020.08", True),
        SwitchEntry("switch.replay.020.09", "module", "module.replay.020.09", True),
        SwitchEntry("switch.replay.020.10", "route", "route.replay.020.10", True),
        SwitchEntry("switch.replay.020.11", "boundary", "boundary.replay.020.11", True),
        SwitchEntry("switch.replay.020.12", "module", "module.replay.020.12", True),
        SwitchEntry("switch.replay.020.13", "route", "route.replay.020.13", True),
        SwitchEntry("switch.replay.020.14", "boundary", "boundary.replay.020.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.020.01": False,
        "switch.replay.020.02": "bad",
        "route.replay.020.03": True,
        "switch.replay.020.04": False,
        "route.replay.020.05": "bad",
        "switch.replay.020.06": True,
        "route.replay.020.07": False,
        "switch.replay.020.08": "bad",
        "route.replay.020.09": True,
        "switch.replay.020.10": False,
        "route.replay.020.11": "bad",
        "switch.replay.020.12": True,
        "route.replay.020.13": False,
        "switch.replay.020.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_020",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
