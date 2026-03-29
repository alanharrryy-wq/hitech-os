from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Protocol

from .models import CloudflareGuardianState, GuardianHealthReport, ZoneSnapshot


class HistoryRunsWriter(Protocol):
    def append(
        self,
        run_id: str,
        producer: str,
        status: str,
        actor: str,
        correlation_id: str,
        details: dict[str, str] | None = None,
    ) -> object:
        pass


class CloudflareGuardianRuntime:
    """Migrated Cloudflare Guardian product runtime without host scraping."""

    product_id = "cloudflare_guardian"
    contribution_id = "contrib.cloudflare_guardian.main_surface"
    slot_id = "primary_workspace"
    surface_kind = "panel"

    def __init__(self, history_runs: HistoryRunsWriter | None = None) -> None:
        self._history_runs = history_runs
        self._state = CloudflareGuardianState.REGISTERED
        self._snapshots: list[ZoneSnapshot] = []
        self._last_report: GuardianHealthReport | None = None

    @property
    def state(self) -> CloudflareGuardianState:
        return self._state

    @property
    def last_report(self) -> GuardianHealthReport | None:
        return self._last_report

    def prepare(self) -> CloudflareGuardianState:
        self._state = CloudflareGuardianState.PREPARED
        return self._state

    def activate(self) -> CloudflareGuardianState:
        self._require_state(CloudflareGuardianState.PREPARED, CloudflareGuardianState.SUSPENDED)
        self._state = CloudflareGuardianState.ACTIVE
        return self._state

    def suspend(self) -> CloudflareGuardianState:
        self._require_state(CloudflareGuardianState.ACTIVE)
        self._state = CloudflareGuardianState.SUSPENDED
        return self._state

    def dispose(self) -> CloudflareGuardianState:
        if self._state is CloudflareGuardianState.DISPOSED:
            return self._state
        self._state = CloudflareGuardianState.DISPOSING
        self._snapshots.clear()
        self._last_report = None
        self._state = CloudflareGuardianState.DISPOSED
        return self._state

    def ingest_snapshots(self, snapshots: list[ZoneSnapshot]) -> None:
        self._require_state(CloudflareGuardianState.ACTIVE, CloudflareGuardianState.SUSPENDED)
        self._snapshots = list(snapshots)

    def evaluate_health(self, actor: str, correlation_id: str) -> GuardianHealthReport:
        self._require_state(CloudflareGuardianState.ACTIVE)
        total = len(self._snapshots)
        healthy = 0
        degraded = 0
        unhealthy = 0
        highest_latency = 0
        error_total = 0.0
        for snapshot in self._snapshots:
            highest_latency = max(highest_latency, snapshot.latency_ms)
            error_total += snapshot.error_rate
            score = _zone_risk(snapshot)
            if score == "healthy":
                healthy += 1
            elif score == "degraded":
                degraded += 1
            else:
                unhealthy += 1
        average_error = (error_total / total) if total > 0 else 0.0
        risk_level = _overall_risk(total, degraded, unhealthy)
        report = GuardianHealthReport(
            total_zones=total,
            healthy_zones=healthy,
            degraded_zones=degraded,
            unhealthy_zones=unhealthy,
            highest_latency_ms=highest_latency,
            average_error_rate=round(average_error, 4),
            risk_level=risk_level,
            generated_at_utc=datetime.now(tz=timezone.utc).isoformat(),
        )
        self._last_report = report
        if self._history_runs is not None:
            self._history_runs.append(
                run_id=f"cloudflare_guardian:{report.generated_at_utc}",
                producer=self.product_id,
                status="finished",
                actor=actor,
                correlation_id=correlation_id,
                details={
                    "total_zones": str(report.total_zones),
                    "risk_level": report.risk_level,
                    "unhealthy_zones": str(report.unhealthy_zones),
                },
            )
        return report

    def contribution_actions(self) -> dict[str, Callable[[], object]]:
        return {"refresh_radar": self._refresh_radar_action}

    def _refresh_radar_action(self) -> dict[str, object]:
        report = self._last_report
        if report is None:
            report = self.evaluate_health(
                actor="cloudflare_guardian",
                correlation_id="cloudflare-guardian-refresh",
            )
        return {
            "total_zones": report.total_zones,
            "healthy_zones": report.healthy_zones,
            "degraded_zones": report.degraded_zones,
            "unhealthy_zones": report.unhealthy_zones,
            "highest_latency_ms": report.highest_latency_ms,
            "average_error_rate": report.average_error_rate,
            "risk_level": report.risk_level,
            "generated_at_utc": report.generated_at_utc,
        }

    def _require_state(self, *states: CloudflareGuardianState) -> None:
        if self._state not in states:
            expected = ", ".join(state.value for state in states)
            raise RuntimeError(
                f"invalid cloudflare_guardian state '{self._state.value}', expected one of: {expected}"
            )


def _zone_risk(snapshot: ZoneSnapshot) -> str:
    if snapshot.status.lower() == "down":
        return "unhealthy"
    if snapshot.error_rate >= 0.1 or snapshot.latency_ms >= 1200:
        return "unhealthy"
    if snapshot.error_rate >= 0.03 or snapshot.latency_ms >= 700:
        return "degraded"
    return "healthy"


def _overall_risk(total: int, degraded: int, unhealthy: int) -> str:
    if total == 0:
        return "unknown"
    if unhealthy > 0:
        return "high"
    if degraded > 0:
        return "medium"
    return "low"
