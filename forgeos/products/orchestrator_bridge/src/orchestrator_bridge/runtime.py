from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Protocol

from .models import (
    OrchestratorBridgeState,
    WorkflowRunReport,
    WorkflowStep,
    WorkflowStepResult,
)


class ProcessExecutionRunner(Protocol):
    def execute(
        self,
        command: list[str],
        actor: str,
        correlation_id: str,
        timeout_seconds: float = 30.0,
    ) -> object:
        pass


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


class OrchestratorBridgeRuntime:
    """Migrated orchestrator product delegating process supervision to commons."""

    product_id = "orchestrator_bridge"
    contribution_id = "contrib.orchestrator_bridge.main_surface"
    slot_id = "primary_workspace"
    surface_kind = "panel"

    def __init__(
        self,
        process_runner: ProcessExecutionRunner,
        history_runs: HistoryRunsWriter | None = None,
    ) -> None:
        self._process_runner = process_runner
        self._history_runs = history_runs
        self._state = OrchestratorBridgeState.REGISTERED
        self._workflows: dict[str, list[WorkflowStep]] = {}
        self._last_report: WorkflowRunReport | None = None

    @property
    def state(self) -> OrchestratorBridgeState:
        return self._state

    @property
    def last_report(self) -> WorkflowRunReport | None:
        return self._last_report

    def prepare(self) -> OrchestratorBridgeState:
        self._state = OrchestratorBridgeState.PREPARED
        return self._state

    def activate(self) -> OrchestratorBridgeState:
        self._require_state(OrchestratorBridgeState.PREPARED, OrchestratorBridgeState.SUSPENDED)
        self._state = OrchestratorBridgeState.ACTIVE
        return self._state

    def suspend(self) -> OrchestratorBridgeState:
        self._require_state(OrchestratorBridgeState.ACTIVE)
        self._state = OrchestratorBridgeState.SUSPENDED
        return self._state

    def dispose(self) -> OrchestratorBridgeState:
        if self._state is OrchestratorBridgeState.DISPOSED:
            return self._state
        self._state = OrchestratorBridgeState.DISPOSING
        self._workflows.clear()
        self._last_report = None
        self._state = OrchestratorBridgeState.DISPOSED
        return self._state

    def register_workflow(self, workflow_id: str, steps: list[WorkflowStep]) -> None:
        self._require_state(
            OrchestratorBridgeState.PREPARED,
            OrchestratorBridgeState.ACTIVE,
            OrchestratorBridgeState.SUSPENDED,
        )
        self._workflows[workflow_id] = list(steps)

    def run_workflow(
        self,
        workflow_id: str,
        actor: str,
        correlation_id: str,
    ) -> WorkflowRunReport:
        self._require_state(OrchestratorBridgeState.ACTIVE)
        steps = self._workflows.get(workflow_id)
        if steps is None:
            raise RuntimeError(f"workflow '{workflow_id}' is not registered")

        results: list[WorkflowStepResult] = []
        completed = 0
        failed = 0
        timed_out = 0
        total_duration_ms = 0
        for step in steps:
            execution = self._process_runner.execute(
                command=list(step.command),
                actor=actor,
                correlation_id=f"{correlation_id}:{step.step_id}",
                timeout_seconds=step.timeout_seconds,
            )
            status = getattr(execution, "status", "failed")
            duration_ms = int(getattr(execution, "duration_ms", 0))
            return_code = getattr(execution, "return_code", None)
            total_duration_ms += duration_ms
            if status == "finished":
                completed += 1
            elif status == "timed_out":
                timed_out += 1
            else:
                failed += 1
            results.append(
                WorkflowStepResult(
                    step_id=step.step_id,
                    status=status,
                    return_code=return_code,
                    duration_ms=duration_ms,
                )
            )

        if failed > 0:
            overall = "failed"
        elif timed_out > 0:
            overall = "timed_out"
        else:
            overall = "finished"

        report = WorkflowRunReport(
            workflow_id=workflow_id,
            total_steps=len(results),
            completed_steps=completed,
            failed_steps=failed,
            timed_out_steps=timed_out,
            overall_status=overall,
            total_duration_ms=total_duration_ms,
            generated_at_utc=datetime.now(tz=timezone.utc).isoformat(),
        )
        self._last_report = report

        if self._history_runs is not None:
            self._history_runs.append(
                run_id=f"orchestrator_bridge:{report.generated_at_utc}",
                producer=self.product_id,
                status=overall,
                actor=actor,
                correlation_id=correlation_id,
                details={
                    "workflow_id": workflow_id,
                    "total_steps": str(report.total_steps),
                    "completed_steps": str(report.completed_steps),
                    "failed_steps": str(report.failed_steps),
                    "timed_out_steps": str(report.timed_out_steps),
                },
            )
        return report

    def contribution_actions(self) -> dict[str, Callable[[], object]]:
        return {"refresh_last_run": self._refresh_last_run_action}

    def _refresh_last_run_action(self) -> dict[str, object]:
        report = self._last_report
        if report is None:
            return {
                "workflow_id": None,
                "overall_status": "no_runs",
                "total_steps": 0,
            }
        return {
            "workflow_id": report.workflow_id,
            "total_steps": report.total_steps,
            "completed_steps": report.completed_steps,
            "failed_steps": report.failed_steps,
            "timed_out_steps": report.timed_out_steps,
            "overall_status": report.overall_status,
            "total_duration_ms": report.total_duration_ms,
            "generated_at_utc": report.generated_at_utc,
        }

    def _require_state(self, *states: OrchestratorBridgeState) -> None:
        if self._state not in states:
            expected = ", ".join(state.value for state in states)
            raise RuntimeError(
                f"invalid orchestrator_bridge state '{self._state.value}', expected one of: {expected}"
            )
