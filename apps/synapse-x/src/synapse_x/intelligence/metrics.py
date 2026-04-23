from typing import Any


def totals(metrics: dict[str, Any]) -> dict[str, int]:
    payload = metrics.get("totals")
    if not isinstance(payload, dict):
        return {}
    return {str(key): int(value) for key, value in payload.items()}
