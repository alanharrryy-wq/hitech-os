#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Small ranking helpers used by policy-facing diagnostic outputs."""

from typing import Any

_SEVERITY_ORDER = {
    'info': 1,
    'warn': 2,
    'warning': 2,
    'error': 3,
    'critical': 4,
}


def severity_rank(value: str | None) -> int:
    return _SEVERITY_ORDER.get(str(value or 'info').strip().lower(), 0)


def sort_finding_rows(rows: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    ordered = sorted(
        [dict(item) for item in list(rows or [])],
        key=lambda item: (
            severity_rank(str(item.get('severity') or 'info')),
            float(item.get('confidence') or 0.0),
            str(item.get('title') or '').lower(),
        ),
        reverse=True,
    )
    return ordered[: max(0, int(limit))]
