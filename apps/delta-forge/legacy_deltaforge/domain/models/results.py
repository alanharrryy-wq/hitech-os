from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from domain.ids import SessionId, parse_session_id
from domain.models.process_report import ProcessReport


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
class BaseResult:
    ok: bool
    summary: str
    status: str = "ok"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    touched_files: list[str] = field(default_factory=list)
    backups: list[dict[str, str]] = field(default_factory=list)
    rollback_token: str = ""
    duration_ms: int = 0
    process: ProcessReport | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    session_id: SessionId | str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.session_id is not None:
            raw = str(self.session_id).strip()
            self.session_id = parse_session_id(raw) if raw else None

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "status": self.status,
            "summary": self.summary,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "touched_files": list(self.touched_files),
            "backups": list(self.backups),
            "rollback_token": self.rollback_token,
            "duration_ms": self.duration_ms,
            "process": None if self.process is None else self.process.as_dict(),
            "payload": dict(self.payload),
            "session_id": None if self.session_id is None else str(self.session_id),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(slots=True)
class ValidationResult(BaseResult):
    issues: list[ValidationIssue] = field(default_factory=list)
    operations_count: int = 0


@dataclass(slots=True)
class ApplyChange:
    path: str
    status: str
    detail: str


@dataclass(slots=True)
class ApplyResult(BaseResult):
    changes: list[ApplyChange] = field(default_factory=list)


@dataclass(slots=True)
class RollbackResult(BaseResult):
    restored_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RefreshResult(BaseResult):
    metadata: dict[str, Any] = field(default_factory=dict)
