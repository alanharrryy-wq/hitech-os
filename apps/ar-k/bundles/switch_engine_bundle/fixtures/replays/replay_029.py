"""Replay builder 029 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.029.01", "route", "route.replay.029.01", False),
        SwitchEntry("switch.replay.029.02", "boundary", "boundary.replay.029.02", True),
        SwitchEntry("switch.replay.029.03", "module", "module.replay.029.03", False),
        SwitchEntry("switch.replay.029.04", "route", "route.replay.029.04", True),
        SwitchEntry("switch.replay.029.05", "boundary", "boundary.replay.029.05", False),
        SwitchEntry("switch.replay.029.06", "module", "module.replay.029.06", True),
        SwitchEntry("switch.replay.029.07", "route", "route.replay.029.07", False),
        SwitchEntry("switch.replay.029.08", "boundary", "boundary.replay.029.08", True),
        SwitchEntry("switch.replay.029.09", "module", "module.replay.029.09", False),
        SwitchEntry("switch.replay.029.10", "route", "route.replay.029.10", True),
        SwitchEntry("switch.replay.029.11", "boundary", "boundary.replay.029.11", False),
        SwitchEntry("switch.replay.029.12", "module", "module.replay.029.12", True),
        SwitchEntry("switch.replay.029.13", "route", "route.replay.029.13", False),
        SwitchEntry("switch.replay.029.14", "boundary", "boundary.replay.029.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.029.01": False,
        "switch.replay.029.02": "bad",
        "route.replay.029.03": True,
        "switch.replay.029.04": False,
        "route.replay.029.05": "bad",
        "switch.replay.029.06": True,
        "route.replay.029.07": False,
        "switch.replay.029.08": "bad",
        "route.replay.029.09": True,
        "switch.replay.029.10": False,
        "route.replay.029.11": "bad",
        "switch.replay.029.12": True,
        "route.replay.029.13": False,
        "switch.replay.029.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_029",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
