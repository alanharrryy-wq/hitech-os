"""Scaffold for modular Git Sentinel.

Origin:
    tools/hos/git_sentinel/cli_sentinel.py

Target role:
    application layer / entrypoints / ui

Status:
    Scaffold only. Legacy implementation remains the source of truth.
"""

from __future__ import annotations

LEGACY_SOURCE = 'tools/hos/git_sentinel/cli_sentinel.py'
LEGACY_MODULE = 'cli_sentinel'
MIGRATION_STATUS = "not_started"


def module_summary() -> dict[str, str]:
    return {
        "legacy_source": LEGACY_SOURCE,
        "legacy_module": LEGACY_MODULE,
        "migration_status": MIGRATION_STATUS,
    }
