from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class CanonicalRecord:
    session_id: str
    timestamp_utc: str
    record_type: str
    source_path: str
    source_hash: str
    title: str = ""
    summary: str = ""
    events: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    tools: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class FileFingerprint:
    path: str
    size_bytes: int
    mtime_utc: str
    content_hash: str
