from typing import Any


def sequence_patterns_from_metrics(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    rows = metrics.get("sequence_patterns")
    if isinstance(rows, list):
        return [dict(item) for item in rows]
    return []
