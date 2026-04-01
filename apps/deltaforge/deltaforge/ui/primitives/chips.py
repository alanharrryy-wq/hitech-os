from __future__ import annotations

# Legacy shim: canonical chip/status primitives live in chip.py and status_pill.py
from deltaforge.ui.primitives.chip import Chip
from deltaforge.ui.primitives.status_pill import StatusPill

ChipLabel = Chip

__all__ = ["ChipLabel", "StatusPill"]
