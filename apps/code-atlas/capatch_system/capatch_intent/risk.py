from __future__ import annotations

from typing import Any


def score_patch_risk(*, files: list[str], operations: list[dict[str, Any]] | None = None, visual: bool = False) -> dict[str, Any]:
    operations = operations or []
    score = 0
    reasons: list[str] = []
    if len(files) > 1:
        score += min(20, len(files) * 2)
        reasons.append('multi-file patch')
    if len(operations) > 12:
        score += 20
        reasons.append('many operations')
    if any(str(path).endswith(('.css', '.tsx', '.jsx')) for path in files):
        score += 10
        reasons.append('ui-facing files')
    if visual:
        score += 20
        reasons.append('visual intent')
    if any('global' in str(path).lower() and str(path).endswith('.css') for path in files):
        score += 25
        reasons.append('global css')
    level = 'low'
    if score >= 70:
        level = 'critical'
    elif score >= 45:
        level = 'high'
    elif score >= 20:
        level = 'medium'
    return {'score': score, 'level': level, 'reasons': reasons}
