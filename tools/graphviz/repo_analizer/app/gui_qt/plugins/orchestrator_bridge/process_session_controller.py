from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Literal, Tuple

SessionState = Literal[
    "ready",
    "validating",
    "running",
    "failed",
    "blocked",
    "succeeded",
    "cancelled",
]


@dataclass(slots=True)
class ProcessSessionSnapshot:
    state: SessionState = "ready"
    run_in_progress: bool = False
    timeout_triggered: bool = False
    terminal_error_handled: bool = False
    current_payload: Dict[str, Any] = field(default_factory=dict)
    last_launched_payload: Dict[str, Any] = field(default_factory=dict)
    transition_count: int = 0
    last_error: str = ""
    last_reason: str = ""


class ProcessSessionController:
    """Non-visual runtime state machine for orchestrator process sessions."""

    def __init__(
        self,
        *,
        logger: Callable[[str], None] | None = None,
        transition_notifier: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._snapshot = ProcessSessionSnapshot()
        self._logger = logger
        self._transition_notifier = transition_notifier

    @property
    def snapshot(self) -> ProcessSessionSnapshot:
        return self._snapshot

    def begin_launch(self, payload: Dict[str, Any]) -> Tuple[bool, str]:
        if self._snapshot.run_in_progress:
            return False, "run already in progress"
        normalized_payload = dict(payload or {})
        if not normalized_payload:
            self.mark_blocked("empty-payload")
            return False, "empty payload"
        self._snapshot.current_payload = normalized_payload
        self._snapshot.last_launched_payload = dict(normalized_payload)
        self._snapshot.timeout_triggered = False
        self._snapshot.terminal_error_handled = False
        self._set_state("validating", run_in_progress=True, reason="begin-launch")
        return True, "ok"

    def mark_ready(self, *, reason: str = "ready") -> None:
        if self._snapshot.state == "ready" and not self._snapshot.run_in_progress:
            return
        self._snapshot.timeout_triggered = False
        self._snapshot.terminal_error_handled = False
        self._set_state("ready", run_in_progress=False, reason=reason)

    def mark_started(self) -> None:
        self._set_state("running", run_in_progress=True, reason="process-started")

    def mark_startup_timeout(self) -> None:
        self._snapshot.timeout_triggered = True
        if self._snapshot.run_in_progress:
            self._set_state("failed", run_in_progress=True, reason="startup-timeout")

    def mark_run_timeout(self) -> None:
        self._snapshot.timeout_triggered = True
        if self._snapshot.run_in_progress:
            self._set_state("failed", run_in_progress=True, reason="run-timeout")

    def mark_process_error(self, error_code: Any, *, process_not_running: bool) -> bool:
        self._snapshot.last_error = str(error_code)
        if (
            not self._snapshot.run_in_progress
            or self._snapshot.terminal_error_handled
            or not process_not_running
        ):
            return False
        self._snapshot.terminal_error_handled = True
        self._set_state("failed", run_in_progress=False, reason=f"process-error:{error_code}")
        return True

    def mark_finished(self, normalized_status: str) -> None:
        status = str(normalized_status or "").strip().lower()
        if status in {"success", "reused", "succeeded"}:
            status = "succeeded"
        elif status not in {"blocked", "failed"}:
            status = "failed"
        self._snapshot.terminal_error_handled = False
        self._snapshot.timeout_triggered = False
        self._set_state(status, run_in_progress=False, reason=f"finished:{status}")

    def mark_blocked(self, reason: str) -> None:
        self._snapshot.terminal_error_handled = False
        self._snapshot.timeout_triggered = False
        self._set_state("blocked", run_in_progress=False, reason=reason or "blocked")

    def cancel(self, *, reason: str = "cancelled") -> None:
        self._snapshot.timeout_triggered = False
        self._snapshot.terminal_error_handled = False
        self._set_state("cancelled", run_in_progress=False, reason=reason)

    def restore_last_payload(
        self,
        payload: Dict[str, Any],
        *,
        validator: Callable[[Dict[str, Any]], list[str]] | None = None,
    ) -> Tuple[bool, str]:
        data = dict(payload or {})
        if not data:
            return False, "empty payload"
        if callable(validator):
            errors = validator(data)
            if errors:
                self._set_state("blocked", run_in_progress=False, reason="restore-invalid")
                return False, errors[0]
        self._snapshot.last_launched_payload = data
        self._log("restore:last_payload")
        return True, "ok"

    def _set_state(self, state: SessionState, *, run_in_progress: bool, reason: str) -> None:
        prev = self._snapshot.state
        self._snapshot.state = state
        self._snapshot.run_in_progress = bool(run_in_progress)
        self._snapshot.last_reason = str(reason or "")
        self._snapshot.transition_count += 1
        payload = {
            "previous_state": prev,
            "state": state,
            "run_in_progress": self._snapshot.run_in_progress,
            "reason": self._snapshot.last_reason,
            "transition_count": self._snapshot.transition_count,
            "timeout_triggered": self._snapshot.timeout_triggered,
            "terminal_error_handled": self._snapshot.terminal_error_handled,
        }
        self._log(
            "session:{prev}->{next_state} running={running} reason={reason}".format(
                prev=prev,
                next_state=state,
                running=self._snapshot.run_in_progress,
                reason=self._snapshot.last_reason,
            )
        )
        self._notify_transition(payload)

    def _log(self, message: str) -> None:
        if callable(self._logger):
            try:
                self._logger(message)
            except Exception:
                return

    def _notify_transition(self, payload: dict[str, Any]) -> None:
        if not callable(self._transition_notifier):
            return
        try:
            self._transition_notifier(dict(payload))
        except Exception:
            return


__all__ = [
    "ProcessSessionController",
    "ProcessSessionSnapshot",
    "SessionState",
]
