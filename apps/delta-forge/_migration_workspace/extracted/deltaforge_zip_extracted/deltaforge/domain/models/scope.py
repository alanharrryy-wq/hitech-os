from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum

from domain.ids import ScopeId, new_scope_id, parse_scope_id


class ScopeKind(str, Enum):
    SINGLE_FILE = "single_file"
    MULTI_FILE = "multi_file"
    DIRECTORY = "directory"
    FILTERED_SELECTION = "filtered_selection"


@dataclass(slots=True)
class ScopeSelection:
    scope_id: ScopeId | str = field(default_factory=new_scope_id)
    kind: ScopeKind = ScopeKind.FILTERED_SELECTION
    source: str = "unknown"
    targets: list[str] = field(default_factory=list)
    resolved_paths: list[str] = field(default_factory=list)
    watch_paths: list[str] = field(default_factory=list)
    root_dir: str = ""
    filters: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.scope_id = parse_scope_id(self.scope_id)
        self.kind = ScopeKind(self.kind)
        normalized_targets = self._normalize_paths(self.resolved_paths or self.targets)
        self.targets = list(normalized_targets)
        self.resolved_paths = list(normalized_targets)
        self.watch_paths = self._normalize_paths(self.watch_paths or self.resolved_paths)

        if not self.root_dir and self.resolved_paths:
            self.root_dir = self._resolve_root_dir(self.resolved_paths)

    @property
    def count(self) -> int:
        return len(self.resolved_paths)

    @property
    def is_empty(self) -> bool:
        return self.count == 0

    def clear(self) -> None:
        self.kind = ScopeKind.FILTERED_SELECTION
        self.source = "cleared"
        self.targets = []
        self.resolved_paths = []
        self.watch_paths = []
        self.root_dir = ""
        self.filters = []

    @classmethod
    def for_single_file(
        cls,
        path: str,
        *,
        source: str = "manual_single_file",
        watch_paths: list[str] | None = None,
    ) -> "ScopeSelection":
        normalized = cls._normalize_paths([path])
        return cls(
            kind=ScopeKind.SINGLE_FILE,
            source=source,
            targets=list(normalized),
            resolved_paths=list(normalized),
            watch_paths=list(watch_paths or normalized),
            root_dir=cls._resolve_root_dir(normalized),
        )

    @classmethod
    def for_multi_file(
        cls,
        paths: list[str],
        *,
        source: str = "manual_multi_file",
        watch_paths: list[str] | None = None,
    ) -> "ScopeSelection":
        normalized = cls._normalize_paths(paths)
        return cls(
            kind=ScopeKind.MULTI_FILE,
            source=source,
            targets=list(normalized),
            resolved_paths=list(normalized),
            watch_paths=list(watch_paths or normalized),
            root_dir=cls._resolve_root_dir(normalized),
        )

    @classmethod
    def for_directory(
        cls,
        directory_path: str,
        *,
        source: str = "manual_directory",
        watch_paths: list[str] | None = None,
    ) -> "ScopeSelection":
        normalized = cls._normalize_paths([directory_path])
        root = normalized[0] if normalized else ""
        return cls(
            kind=ScopeKind.DIRECTORY,
            source=source,
            targets=list(normalized),
            resolved_paths=list(normalized),
            watch_paths=list(watch_paths or normalized),
            root_dir=root,
        )

    @classmethod
    def for_filtered_selection(
        cls,
        paths: list[str],
        *,
        filters: list[str] | None = None,
        source: str = "filtered_selection",
        watch_paths: list[str] | None = None,
    ) -> "ScopeSelection":
        normalized = cls._normalize_paths(paths)
        return cls(
            kind=ScopeKind.FILTERED_SELECTION,
            source=source,
            targets=list(normalized),
            resolved_paths=list(normalized),
            watch_paths=list(watch_paths or normalized),
            root_dir=cls._resolve_root_dir(normalized),
            filters=list(filters or []),
        )

    @classmethod
    def from_targets(
        cls,
        targets: list[str],
        *,
        root_dir: str = "",
        source: str = "legacy_targets",
        watch_paths: list[str] | None = None,
        filters: list[str] | None = None,
    ) -> "ScopeSelection":
        normalized = cls._normalize_paths(targets)
        kind = cls._resolve_kind(normalized, filters=filters)
        resolved_root = root_dir or cls._resolve_root_dir(normalized)
        return cls(
            kind=kind,
            source=source,
            targets=list(normalized),
            resolved_paths=list(normalized),
            watch_paths=list(watch_paths or normalized),
            root_dir=resolved_root,
            filters=list(filters or []),
        )

    @staticmethod
    def _normalize_paths(paths: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for raw in paths:
            value = str(raw or "").strip()
            if not value:
                continue
            canonical = os.path.normpath(value)
            if canonical in seen:
                continue
            seen.add(canonical)
            normalized.append(canonical)
        return normalized

    @staticmethod
    def _resolve_root_dir(paths: list[str]) -> str:
        if not paths:
            return ""
        if len(paths) == 1:
            return paths[0]
        try:
            return os.path.commonpath(paths)
        except ValueError:
            return os.path.dirname(paths[0])

    @classmethod
    def _resolve_kind(
        cls,
        paths: list[str],
        *,
        filters: list[str] | None,
    ) -> ScopeKind:
        if filters:
            return ScopeKind.FILTERED_SELECTION
        if len(paths) <= 1:
            if paths and os.path.isdir(paths[0]):
                return ScopeKind.DIRECTORY
            return ScopeKind.SINGLE_FILE if paths else ScopeKind.FILTERED_SELECTION
        return ScopeKind.MULTI_FILE
