from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class PatchContext:
    root_dir: Path
    backup_dir: Path
    checkpoint_dir: Path
    dry_run: bool
    auto_support: bool
    requested_by: str | None = None
    invocation_mode: str = "patch-run"
    run_id: str | None = None
