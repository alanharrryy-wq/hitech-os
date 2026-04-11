#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Builtin verifier for command-based Autofix proposals."""

from typing import Any


def run_command_exit_zero(target_files: list[str], ctx: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [dict(item or {}) for item in list((ctx or {}).get('command_results') or [])]
    if not rows:
        return [
            {
                'verifier_id': 'command-exit-zero',
                'ok': False,
                'title': 'Command exit status unavailable',
                'detail': 'No command_results were present in the verifier context.',
                'metrics': {'command_count': 0, 'failed_count': 0, 'blocked_count': 0},
            }
        ]

    blocked = [row for row in rows if not bool(row.get('allowlisted', False))]
    failed = [row for row in rows if bool(row.get('allowlisted', False)) and row.get('returncode') not in {0, None}]
    ok = not blocked and not failed
    detail_parts = [f"commands={len(rows)}", f"failed={len(failed)}", f"blocked={len(blocked)}"]
    if failed:
        detail_parts.append('failed_commands=' + ', '.join(str(item.get('command') or '') for item in failed[:3]))
    if blocked:
        detail_parts.append('blocked_commands=' + ', '.join(str(item.get('command') or '') for item in blocked[:3]))
    return [
        {
            'verifier_id': 'command-exit-zero',
            'ok': ok,
            'title': 'Command exit codes are zero',
            'detail': '; '.join(detail_parts),
            'metrics': {
                'command_count': len(rows),
                'failed_count': len(failed),
                'blocked_count': len(blocked),
            },
        }
    ]
