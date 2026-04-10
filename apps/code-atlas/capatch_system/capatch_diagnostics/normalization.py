from __future__ import annotations

"""Normalización canónica para payloads del runtime diagnóstico."""

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from ._contracts import DEFAULT_MAX_FIX_PROPOSALS_TO_EXECUTE, PRIORITIES, RISK_LEVELS, RISK_TIERS, SEVERITIES


SEVERITY_ALIASES = {
    "warning": "warn",
    "warn": "warn",
    "error": "error",
    "critical": "critical",
    "info": "info",
}
PRIORITY_ALIASES = {value: value for value in PRIORITIES}
RISK_LEVEL_ALIASES = {value: value for value in RISK_LEVELS}
RISK_TIER_ALIASES = {value: value for value in RISK_TIERS}


def normalize_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {key: normalize_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): normalize_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [normalize_jsonable(item) for item in value]
    return value


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def normalize_severity(value: Any, default: str = "info") -> str:
    normalized = SEVERITY_ALIASES.get(str(value or default).strip().lower(), default)
    return normalized if normalized in SEVERITIES else default


def normalize_priority(value: Any, default: str = "normal") -> str:
    normalized = PRIORITY_ALIASES.get(str(value or default).strip().lower(), default)
    return normalized if normalized in PRIORITIES else default


def normalize_risk_level(value: Any, default: str = "low") -> str:
    normalized = RISK_LEVEL_ALIASES.get(str(value or default).strip().lower(), default)
    return normalized if normalized in RISK_LEVELS else default


def normalize_risk_tier(value: Any, default: str = "guarded") -> str:
    normalized = RISK_TIER_ALIASES.get(str(value or default).strip().lower(), default)
    return normalized if normalized in RISK_TIERS else default


def trim_text(value: Any, *, default: str = "") -> str:
    text = str(value or default)
    return text.strip()


def default_fix_limit(value: Any) -> int:
    try:
        return max(1, int(value or DEFAULT_MAX_FIX_PROPOSALS_TO_EXECUTE))
    except Exception:
        return DEFAULT_MAX_FIX_PROPOSALS_TO_EXECUTE
