from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RuntimeConfig:
    root: Path
    target: Path
    out: Path
    kernel_version: str = "1.0.0"
    strict: bool = True
    switch_overrides: dict[str, bool] = field(default_factory=dict)
