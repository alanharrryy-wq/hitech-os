from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SessionRecorder:
    session_id: str
    output_dir: Path
    purpose: str = ""
    failure_severity: str = "major"
    required_capabilities: list[int] = field(default_factory=list)
    expected_checkpoints: list[str] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    checkpoints: dict[str, dict[str, Any]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    started_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ended_at_utc: str = ""
    passed: bool = False

    def log_event(self, event_type: str, message: str, **details: Any) -> None:
        event = {
            "at_utc": datetime.now(timezone.utc).isoformat(),
            "type": str(event_type or "event"),
            "message": str(message or ""),
            "details": details or {},
        }
        self.events.append(event)

    def checkpoint(
        self,
        *,
        checkpoint_id: str,
        snapshot: dict[str, Any],
        screenshot_path: str = "",
    ) -> None:
        payload = {
            "checkpoint_id": str(checkpoint_id or "").strip(),
            "snapshot": snapshot,
            "screenshot_path": str(screenshot_path or ""),
            "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        self.checkpoints[str(checkpoint_id)] = payload
        self.log_event("checkpoint", f"Checkpoint captured: {checkpoint_id}", checkpoint_id=checkpoint_id)

    def warn(self, message: str) -> None:
        self.warnings.append(str(message))
        self.log_event("warning", message)

    def fail(self, message: str) -> None:
        self.errors.append(str(message))
        self.log_event("error", message)

    def finalize(self, *, passed: bool) -> dict[str, Any]:
        self.ended_at_utc = datetime.now(timezone.utc).isoformat()
        self.passed = bool(passed and not self.errors)
        event_types = sorted({str(item.get("type", "")).strip() for item in self.events if str(item.get("type", "")).strip()})
        manifest = {
            "session_id": self.session_id,
            "purpose": self.purpose,
            "failure_severity": self.failure_severity,
            "required_capabilities": [int(item) for item in self.required_capabilities if str(item).strip().isdigit()],
            "expected_checkpoints": [str(item).strip() for item in self.expected_checkpoints if str(item).strip()],
            "started_at_utc": self.started_at_utc,
            "ended_at_utc": self.ended_at_utc,
            "passed": self.passed,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "event_count": len(self.events),
            "event_types": event_types,
            "checkpoint_count": len(self.checkpoints),
            "checkpoints": sorted(self.checkpoints.keys()),
        }
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        (self.output_dir / "events.json").write_text(
            json.dumps(self.events, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        checkpoints_dir = self.output_dir / "checkpoints"
        checkpoints_dir.mkdir(parents=True, exist_ok=True)
        for checkpoint_id, payload in self.checkpoints.items():
            (checkpoints_dir / f"{checkpoint_id}.json").write_text(
                json.dumps(payload, indent=2, ensure_ascii=True),
                encoding="utf-8",
            )
        return manifest
