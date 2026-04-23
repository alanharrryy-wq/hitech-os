"""Replay builder 019 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.019.01", "route", "route.replay.019.01", False),
        SwitchEntry("switch.replay.019.02", "boundary", "boundary.replay.019.02", True),
        SwitchEntry("switch.replay.019.03", "module", "module.replay.019.03", False),
        SwitchEntry("switch.replay.019.04", "route", "route.replay.019.04", True),
        SwitchEntry("switch.replay.019.05", "boundary", "boundary.replay.019.05", False),
        SwitchEntry("switch.replay.019.06", "module", "module.replay.019.06", True),
        SwitchEntry("switch.replay.019.07", "route", "route.replay.019.07", False),
        SwitchEntry("switch.replay.019.08", "boundary", "boundary.replay.019.08", True),
        SwitchEntry("switch.replay.019.09", "module", "module.replay.019.09", False),
        SwitchEntry("switch.replay.019.10", "route", "route.replay.019.10", True),
        SwitchEntry("switch.replay.019.11", "boundary", "boundary.replay.019.11", False),
        SwitchEntry("switch.replay.019.12", "module", "module.replay.019.12", True),
        SwitchEntry("switch.replay.019.13", "route", "route.replay.019.13", False),
        SwitchEntry("switch.replay.019.14", "boundary", "boundary.replay.019.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.019.01": False,
        "switch.replay.019.02": "bad",
        "route.replay.019.03": True,
        "switch.replay.019.04": False,
        "route.replay.019.05": "bad",
        "switch.replay.019.06": True,
        "route.replay.019.07": False,
        "switch.replay.019.08": "bad",
        "route.replay.019.09": True,
        "switch.replay.019.10": False,
        "route.replay.019.11": "bad",
        "switch.replay.019.12": True,
        "route.replay.019.13": False,
        "switch.replay.019.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_019",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
