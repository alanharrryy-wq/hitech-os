#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
@dataclass(slots=True)
class ProjectProfile:
    root: str
    exists: bool
    project_type: str = "unknown"
    languages: list[str] = field(default_factory=list)
    package_manager: str = "unknown"
    frameworks: list[str] = field(default_factory=list)
    config_files: list[str] = field(default_factory=list)
    entrypoints: list[str] = field(default_factory=list)
    source_counts: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    @property
    def root_path(self) -> Path:
        return Path(self.root)
    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root, "exists": self.exists, "project_type": self.project_type,
            "languages": list(self.languages), "package_manager": self.package_manager,
            "frameworks": list(self.frameworks), "config_files": list(self.config_files),
            "entrypoints": list(self.entrypoints), "source_counts": dict(self.source_counts),
            "notes": list(self.notes),
        }
