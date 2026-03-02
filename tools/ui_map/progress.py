from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .io_utils import ensure_directory


@dataclass(frozen=True)
class ProgressPaths:
    run_dir: Path
    events_file: Path
    summary_file: Path


class ProgressLogger:
    def __init__(self, logs_root: Path, run_tag: str, command: str) -> None:
        run_dir = ensure_directory(logs_root / run_tag)
        self.paths = ProgressPaths(
            run_dir=run_dir,
            events_file=run_dir / "events.jsonl",
            summary_file=run_dir / "summary.log",
        )
        self.command = command

    def event(
        self,
        message: str,
        *,
        percent: int | None = None,
        details: dict[str, Any] | None = None,
        level: str = "INFO",
        event_type: str = "step",
    ) -> None:
        payload: dict[str, Any] = {
            "command": self.command,
            "event_type": event_type,
            "level": level,
            "message": message,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        if percent is not None:
            payload["percent"] = int(percent)
        if details:
            payload["details"] = details

        with self.paths.events_file.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")

        summary_parts = [f"[{level}]", message]
        if percent is not None:
            summary_parts.append(f"({percent}%)")
        with self.paths.summary_file.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(" ".join(summary_parts) + "\n")


def default_run_tag() -> str:
    return datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")
