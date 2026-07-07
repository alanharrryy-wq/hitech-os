"""Operational Evidence Atlas public compatibility surface.

This module intentionally keeps legacy entry points alive while the real
implementation lives in the modular operational CLI package.
"""

from __future__ import annotations

from typing import Any

from .cli import run_operational_atlas


def run_operational_evidence(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for older Code Atlas callers."""
    return run_operational_atlas(*args, **kwargs)


def run_operational_evidence_atlas(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for Todo El Show Plus and previous integrations."""
    return run_operational_atlas(*args, **kwargs)


def run(*args: Any, **kwargs: Any) -> Any:
    """Legacy shorthand alias used by earlier operational integrations."""
    return run_operational_atlas(*args, **kwargs)


__all__ = [
    "run_operational_atlas",
    "run_operational_evidence",
    "run_operational_evidence_atlas",
    "run",
]
