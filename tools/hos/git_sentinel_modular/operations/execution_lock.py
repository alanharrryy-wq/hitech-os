"""Scaffold for modular Git Sentinel.

Origin:
    tools/hos/git_sentinel/execution_lock.py

Target role:
    runtime operations

Status:
    Scaffold only. Legacy implementation remains the source of truth.
"""

from __future__ import annotations

LEGACY_SOURCE = 'tools/hos/git_sentinel/execution_lock.py'
LEGACY_MODULE = 'execution_lock'
MIGRATION_STATUS = "not_started"


def module_summary() -> dict[str, str]:
    return {
        "legacy_source": LEGACY_SOURCE,
        "legacy_module": LEGACY_MODULE,
        "migration_status": MIGRATION_STATUS,
    }
