"""Scaffold for modular Git Sentinel.

Origin:
    tools/hos/git_sentinel/ignore_manager.py

Target role:
    shared utilities and contracts

Status:
    Scaffold only. Legacy implementation remains the source of truth.
"""

from __future__ import annotations

LEGACY_SOURCE = 'tools/hos/git_sentinel/ignore_manager.py'
LEGACY_MODULE = 'ignore_manager'
MIGRATION_STATUS = "not_started"


def module_summary() -> dict[str, str]:
    return {
        "legacy_source": LEGACY_SOURCE,
        "legacy_module": LEGACY_MODULE,
        "migration_status": MIGRATION_STATUS,
    }
