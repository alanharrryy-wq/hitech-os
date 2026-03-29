from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict


@dataclass(frozen=True)
class GuardianPolicy:
    max_boot_attempts_per_window: int = 3
    boot_window_hours: int = 12
    global_lock_ttl_seconds: int = 1800
    repair_cooldown_seconds: int = 120
    pulse_interval_minutes: int = 5
    startup_delay_seconds: int = 75
    public_probe_timeout_seconds: int = 12
    origin_probe_timeout_seconds: int = 8
    tunnel_validation_timeout_seconds: int = 45
    repair_script_timeout_seconds: int = 180
    repo_analyzer_self_test_timeout_seconds: int = 90
    repo_analyzer_cli_timeout_seconds: int = 30

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def is_boot_window_expired(self, last_attempt_utc: str | None, now: datetime | None = None) -> bool:
        if not last_attempt_utc:
            return True
        current = now or datetime.now(timezone.utc)
        previous = datetime.fromisoformat(last_attempt_utc.replace("Z", "+00:00"))
        return current - previous >= timedelta(hours=self.boot_window_hours)
