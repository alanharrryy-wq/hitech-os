from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass(slots=True)
class EventLogEntry:
    category: str
    message: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class ValidationIssue:
    severity: Literal["info", "warning", "error"]
    message: str
    path: str = ""


@dataclass(slots=True)
class ValidationResult:
    ok: bool
    summary: str
    issues: list[ValidationIssue] = field(default_factory=list)


@dataclass(slots=True)
class ApplyChange:
    path: str
    status: str
    detail: str


@dataclass(slots=True)
class ApplyResult:
    ok: bool
    summary: str
    changes: list[ApplyChange] = field(default_factory=list)
    rollback_token: str = ""


@dataclass(slots=True)
class RollbackResult:
    ok: bool
    summary: str
    restored_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RefreshResult:
    ok: bool
    summary: str
