
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


SEVERITY_WEIGHT = {
    Severity.INFO.value: 0,
    Severity.WARNING.value: 1,
    Severity.ERROR.value: 2,
    Severity.CRITICAL.value: 3,
}


@dataclass(frozen=True)
class GateDecision:
    gate_id: str
    status: str
    reason: str
    max_severity: str


def max_severity(values: list[str]) -> str:
    if not values:
        return Severity.INFO.value
    return max(values, key=lambda item: SEVERITY_WEIGHT[item])


def bundle_status_from_findings(values: list[str]) -> str:
    worst = max_severity(values)
    if worst in {Severity.ERROR.value, Severity.CRITICAL.value}:
        return 'BLOCKED'
    if worst == Severity.WARNING.value:
        return 'WARNING'
    return 'READY'
