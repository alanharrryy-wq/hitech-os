
"""Tiny logging helpers for the self-contained installer."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from core.bundle_constants import LOG_BASENAME_PREFIX


def timestamp_token(now: datetime | None = None) -> str:
    now = now or datetime.now()
    return now.strftime('%y%m%d_%H%M')


def default_log_path(log_dir: Path, now: datetime | None = None) -> Path:
    return log_dir / f"{LOG_BASENAME_PREFIX}{timestamp_token(now)}.log"
