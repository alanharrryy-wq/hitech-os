"""Replay builder 022 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.022.01", "route", "route.replay.022.01", True),
        SwitchEntry("switch.replay.022.02", "boundary", "boundary.replay.022.02", True),
        SwitchEntry("switch.replay.022.03", "module", "module.replay.022.03", True),
        SwitchEntry("switch.replay.022.04", "route", "route.replay.022.04", True),
        SwitchEntry("switch.replay.022.05", "boundary", "boundary.replay.022.05", True),
        SwitchEntry("switch.replay.022.06", "module", "module.replay.022.06", True),
        SwitchEntry("switch.replay.022.07", "route", "route.replay.022.07", True),
        SwitchEntry("switch.replay.022.08", "boundary", "boundary.replay.022.08", True),
        SwitchEntry("switch.replay.022.09", "module", "module.replay.022.09", True),
        SwitchEntry("switch.replay.022.10", "route", "route.replay.022.10", True),
        SwitchEntry("switch.replay.022.11", "boundary", "boundary.replay.022.11", True),
        SwitchEntry("switch.replay.022.12", "module", "module.replay.022.12", True),
        SwitchEntry("switch.replay.022.13", "route", "route.replay.022.13", True),
        SwitchEntry("switch.replay.022.14", "boundary", "boundary.replay.022.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.022.01": False,
        "switch.replay.022.02": "bad",
        "route.replay.022.03": True,
        "switch.replay.022.04": False,
        "route.replay.022.05": "bad",
        "switch.replay.022.06": True,
        "route.replay.022.07": False,
        "switch.replay.022.08": "bad",
        "route.replay.022.09": True,
        "switch.replay.022.10": False,
        "route.replay.022.11": "bad",
        "switch.replay.022.12": True,
        "route.replay.022.13": False,
        "switch.replay.022.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_022",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
