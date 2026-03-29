from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RepoAnalyzerState(str, Enum):
    REGISTERED = "registered"
    PREPARED = "prepared"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISPOSING = "disposing"
    DISPOSED = "disposed"


@dataclass(frozen=True)
class RepositorySummary:
    root_path: str
    total_files: int
    total_lines: int
    generated_at_utc: str
    extension_counts: dict[str, int]


@dataclass(frozen=True)
class SearchMatch:
    file_path: str
    line_number: int
    line_text: str
