from typing import Any


def timeline_from_session_detail(detail: dict[str, Any]) -> list[dict[str, Any]]:
    timeline = detail.get("timeline")
    if isinstance(timeline, list):
        return [dict(item) for item in timeline]
    return []
