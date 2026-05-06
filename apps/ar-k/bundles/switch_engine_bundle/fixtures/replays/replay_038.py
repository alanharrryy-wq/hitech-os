"""Replay builder 038 for deterministic trace verification."""

from __future__ import annotations

from switch_engine.models import SwitchEntry

def build_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry("switch.replay.038.01", "route", "route.replay.038.01", True),
        SwitchEntry("switch.replay.038.02", "boundary", "boundary.replay.038.02", True),
        SwitchEntry("switch.replay.038.03", "module", "module.replay.038.03", True),
        SwitchEntry("switch.replay.038.04", "route", "route.replay.038.04", True),
        SwitchEntry("switch.replay.038.05", "boundary", "boundary.replay.038.05", True),
        SwitchEntry("switch.replay.038.06", "module", "module.replay.038.06", True),
        SwitchEntry("switch.replay.038.07", "route", "route.replay.038.07", True),
        SwitchEntry("switch.replay.038.08", "boundary", "boundary.replay.038.08", True),
        SwitchEntry("switch.replay.038.09", "module", "module.replay.038.09", True),
        SwitchEntry("switch.replay.038.10", "route", "route.replay.038.10", True),
        SwitchEntry("switch.replay.038.11", "boundary", "boundary.replay.038.11", True),
        SwitchEntry("switch.replay.038.12", "module", "module.replay.038.12", True),
        SwitchEntry("switch.replay.038.13", "route", "route.replay.038.13", True),
        SwitchEntry("switch.replay.038.14", "boundary", "boundary.replay.038.14", True),
    ]

def build_overrides() -> dict[str, object]:
    return {
        "route.replay.038.01": False,
        "switch.replay.038.02": "bad",
        "route.replay.038.03": True,
        "switch.replay.038.04": False,
        "route.replay.038.05": "bad",
        "switch.replay.038.06": True,
        "route.replay.038.07": False,
        "switch.replay.038.08": "bad",
        "route.replay.038.09": True,
        "switch.replay.038.10": False,
        "route.replay.038.11": "bad",
        "switch.replay.038.12": True,
        "route.replay.038.13": False,
        "switch.replay.038.14": "bad",
    }

REPLAY_EXPECTATION = {
    "replay_id": "replay_038",
    "invariants": [
        "sorted switch_id order",
        "stable deterministic hash",
        "precedence path recorded on every trace row",
        "reports_real exclusion stays external to switch output writes",
    ],
}
