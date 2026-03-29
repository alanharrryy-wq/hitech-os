from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CloudflareGuardianState(str, Enum):
    REGISTERED = "registered"
    PREPARED = "prepared"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISPOSING = "disposing"
    DISPOSED = "disposed"


@dataclass(frozen=True)
class ZoneSnapshot:
    zone_id: str
    status: str
    latency_ms: int
    error_rate: float
    checked_at_utc: str


@dataclass(frozen=True)
class GuardianHealthReport:
    total_zones: int
    healthy_zones: int
    degraded_zones: int
    unhealthy_zones: int
    highest_latency_ms: int
    average_error_rate: float
    risk_level: str
    generated_at_utc: str
