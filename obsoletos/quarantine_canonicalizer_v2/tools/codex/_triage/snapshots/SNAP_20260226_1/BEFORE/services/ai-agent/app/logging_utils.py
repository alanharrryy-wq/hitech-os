from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional

from .models import JsonValue, StructuredLogModel


def _normalize_iso_utc(value: Optional[str]) -> str:
    if value is None:
        return datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _stable_details(details: Optional[Dict[str, JsonValue]]) -> Dict[str, JsonValue]:
    if not details:
        return {}
    return {key: details[key] for key in sorted(details.keys())}


def build_log(
    *,
    seq: int,
    level: str,
    event: str,
    message: str,
    at_utc: Optional[str],
    details: Optional[Dict[str, JsonValue]] = None,
) -> StructuredLogModel:
    return StructuredLogModel.model_validate(
        {
            "seq": seq,
            "level": level,
            "event": event,
            "message": message,
            "atUtc": _normalize_iso_utc(at_utc),
            "details": _stable_details(details),
        }
    )
