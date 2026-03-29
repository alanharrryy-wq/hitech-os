from __future__ import annotations

import json
import sys
import threading
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
        self.command = str(command)
        self._lock = threading.Lock()

        # Ensure files exist so downstream tooling always finds them, even on early failure.
        self.paths.events_file.touch(exist_ok=True)
        self.paths.summary_file.touch(exist_ok=True)

    def event(
        self,
        message: str,
        *,
        percent: int | None = None,
        details: dict[str, Any] | None = None,
        level: str = "INFO",
        event_type: str = "step",
    ) -> None:
        level_normalized = self._normalize_level(level)
        event_type_normalized = self._normalize_event_type(event_type)
        timestamp = self._utc_now_iso()
        safe_percent = self._normalize_percent(percent)
        safe_details = self._make_json_safe(details) if details is not None else None

        payload: dict[str, Any] = {
            "command": self.command,
            "event_type": event_type_normalized,
            "level": level_normalized,
            "message": str(message),
            "timestamp_utc": timestamp,
        }
        if safe_percent is not None:
            payload["percent"] = safe_percent
        if safe_details:
            payload["details"] = safe_details

        summary_line = self._build_summary_line(
            message=str(message),
            level=level_normalized,
            percent=safe_percent,
            timestamp=timestamp,
        )

        with self._lock:
            self._safe_append_line(
                self.paths.events_file,
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
            )
            self._safe_append_line(self.paths.summary_file, summary_line)
            self._emit_console(summary_line, safe_details)

    @staticmethod
    def _utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _normalize_level(level: str) -> str:
        normalized = str(level or "INFO").strip().upper()
        return normalized or "INFO"

    @staticmethod
    def _normalize_event_type(event_type: str) -> str:
        normalized = str(event_type or "step").strip().lower()
        return normalized or "step"

    @staticmethod
    def _normalize_percent(percent: int | None) -> int | None:
        if percent is None:
            return None
        try:
            numeric = int(percent)
        except (TypeError, ValueError):
            return None
        return max(0, min(100, numeric))

    @staticmethod
    def _make_json_safe(value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, dict):
            return {str(key): ProgressLogger._make_json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [ProgressLogger._make_json_safe(item) for item in value]
        return repr(value)

    def _build_summary_line(
        self,
        *,
        message: str,
        level: str,
        percent: int | None,
        timestamp: str,
    ) -> str:
        summary_parts = [timestamp, f"[{level}]", f"[{self.command}]", message]
        if percent is not None:
            summary_parts.append(f"({percent}%)")
        return " ".join(summary_parts)

    @staticmethod
    def _safe_append_line(path: Path, line: str) -> None:
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line + "\n")

    @staticmethod
    def _emit_console(summary_line: str, details: dict[str, Any] | None) -> None:
        ProgressLogger._safe_print(summary_line)
        if details:
            ProgressLogger._safe_print(
                json.dumps(details, ensure_ascii=False, sort_keys=True)
            )

    @staticmethod
    def _safe_print(line: str) -> None:
        try:
            print(line, flush=True)
        except UnicodeEncodeError:
            encoding = sys.stdout.encoding or "utf-8"
            fallback = line.encode(encoding, errors="replace").decode(encoding, errors="replace")
            print(fallback, flush=True)


def default_run_tag() -> str:
    return datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")
