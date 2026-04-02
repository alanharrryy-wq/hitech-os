from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from domain.ids import SessionId, parse_session_id


@dataclass(slots=True)
class EventLogEntry:
    category: str
    message: str
    session_id: SessionId | str | None = None
    event_name: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.session_id is not None:
            raw = str(self.session_id).strip()
            self.session_id = parse_session_id(raw) if raw else None


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
    session_id: SessionId | str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.session_id is not None:
            raw = str(self.session_id).strip()
            self.session_id = parse_session_id(raw) if raw else None


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
    session_id: SessionId | str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.session_id is not None:
            raw = str(self.session_id).strip()
            self.session_id = parse_session_id(raw) if raw else None


@dataclass(slots=True)
class RollbackResult:
    ok: bool
    summary: str
    restored_paths: list[str] = field(default_factory=list)
    session_id: SessionId | str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.session_id is not None:
            raw = str(self.session_id).strip()
            self.session_id = parse_session_id(raw) if raw else None


@dataclass(slots=True)
class RefreshResult:
    ok: bool
    summary: str
    session_id: SessionId | str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.session_id is not None:
            raw = str(self.session_id).strip()
            self.session_id = parse_session_id(raw) if raw else None
