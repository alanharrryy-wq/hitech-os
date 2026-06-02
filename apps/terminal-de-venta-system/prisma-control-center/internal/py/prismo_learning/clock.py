# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Deterministic-ish clock helpers used by reports, scoring and evidence freshness."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import os


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def from_timestamp(ts: float | int | None) -> str | None:
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).replace(microsecond=0).isoformat()
    except Exception:
        return None


def age_seconds(path: str | os.PathLike[str]) -> float | None:
    try:
        return max(0.0, datetime.now(timezone.utc).timestamp() - Path(path).stat().st_mtime)
    except Exception:
        return None


def freshness_bucket(modified_at: str | float | int | None) -> str:
    if modified_at is None:
        return "unknown"
    if isinstance(modified_at, (int, float)):
        seconds = max(0.0, datetime.now(timezone.utc).timestamp() - float(modified_at))
    else:
        try:
            parsed = datetime.fromisoformat(str(modified_at).replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            seconds = max(0.0, (datetime.now(timezone.utc) - parsed).total_seconds())
        except Exception:
            return "unknown"
    if seconds <= 3600:
        return "fresh_hour"
    if seconds <= 86400:
        return "fresh_day"
    if seconds <= 604800:
        return "fresh_week"
    if seconds <= 2592000:
        return "month"
    if seconds <= 7776000:
        return "quarter"
    return "old"


def sortable_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
