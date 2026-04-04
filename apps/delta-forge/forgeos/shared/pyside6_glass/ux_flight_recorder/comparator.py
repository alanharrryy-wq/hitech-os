from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


SEVERITY_ORDER = {
    "blocker": 4,
    "major": 3,
    "minor": 2,
    "informational": 1,
}

REQUIRED_SNAPSHOT_KEYS = (
    "active_workspace_id",
    "active_tab_id",
    "workspace_tab_ids",
    "visible_tab_ids",
    "mounted_panel_ids",
    "hidden_panel_ids",
    "slot_assignments",
    "panel_geometries",
    "window_geometry",
    "workspace_bounds",
    "selected_entry_id",
    "picker_open",
    "inspector_visible",
    "runtime_state",
    "data_state",
    "clone_state",
    "dirty_state",
    "lazy_mount_state",
    "budget_counters",
    "current_status",
    "recent_action_trace",
)


@dataclass(slots=True)
class ComparisonDiff:
    session_id: str
    checkpoint_id: str
    severity: str
    code: str
    message: str

    def to_payload(self) -> dict[str, str]:
        return {
            "session_id": self.session_id,
            "checkpoint_id": self.checkpoint_id,
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
        }


def _severity_max(diffs: list[ComparisonDiff]) -> str:
    if not diffs:
        return "informational"
    return max(diffs, key=lambda item: SEVERITY_ORDER.get(item.severity, 0)).severity


def _compare_geometry(
    *,
    session_id: str,
    checkpoint_id: str,
    base_snapshot: dict[str, Any],
    run_snapshot: dict[str, Any],
    tolerance_px: int = 28,
) -> list[ComparisonDiff]:
    diffs: list[ComparisonDiff] = []
    base_geo = base_snapshot.get("panel_geometries", {})
    run_geo = run_snapshot.get("panel_geometries", {})
    if not isinstance(base_geo, dict) or not isinstance(run_geo, dict):
        return diffs
    for panel_id, base_rect in base_geo.items():
        run_rect = run_geo.get(panel_id)
        if not isinstance(base_rect, dict):
            continue
        if not isinstance(run_rect, dict):
            diffs.append(
                ComparisonDiff(
                    session_id=session_id,
                    checkpoint_id=checkpoint_id,
                    severity="major",
                    code="panel_geometry_missing",
                    message=f"Panel geometry missing for '{panel_id}' in run snapshot.",
                )
            )
            continue
        for axis in ("x", "y", "width", "height"):
            base_value = int(base_rect.get(axis, 0))
            run_value = int(run_rect.get(axis, 0))
            delta = abs(run_value - base_value)
            if delta <= tolerance_px:
                continue
            severity = "major" if axis in {"width", "height"} else "minor"
            diffs.append(
                ComparisonDiff(
                    session_id=session_id,
                    checkpoint_id=checkpoint_id,
                    severity=severity,
                    code="panel_geometry_delta",
                    message=f"Panel '{panel_id}' axis '{axis}' drift={delta}px (tol={tolerance_px}px).",
                )
            )
    return diffs


def _ensure_checkpoint_shape(
    *,
    session_id: str,
    checkpoint_id: str,
    snapshot: dict[str, Any],
) -> list[ComparisonDiff]:
    diffs: list[ComparisonDiff] = []
    for key in REQUIRED_SNAPSHOT_KEYS:
        if key in snapshot:
            continue
        diffs.append(
            ComparisonDiff(
                session_id=session_id,
                checkpoint_id=checkpoint_id,
                severity="major",
                code="checkpoint_missing_required_key",
                message=f"Checkpoint '{checkpoint_id}' missing required key '{key}'.",
            )
        )
    return diffs


def _iter_session_ids(
    baseline_sessions: dict[str, Any],
    run_sessions: dict[str, Any],
    required_session_ids: Iterable[str] | None,
) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for session_id in (required_session_ids or []):
        text = str(session_id).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    for source in (baseline_sessions, run_sessions):
        for session_id in source.keys():
            text = str(session_id).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            ordered.append(text)
    return ordered


def compare_semantic_baseline(
    *,
    baseline: dict[str, Any],
    run_payload: dict[str, Any],
    required_session_ids: Iterable[str] | None = None,
    required_capabilities: Iterable[int] | None = None,
) -> dict[str, Any]:
    diffs: list[ComparisonDiff] = []
    baseline_sessions = baseline.get("sessions", {})
    run_sessions = run_payload.get("sessions", {})
    if not isinstance(baseline_sessions, dict):
        baseline_sessions = {}
    if not isinstance(run_sessions, dict):
        run_sessions = {}

    session_ids = _iter_session_ids(
        baseline_sessions=baseline_sessions,
        run_sessions=run_sessions,
        required_session_ids=required_session_ids,
    )
    for session_id in session_ids:
        run_session = run_sessions.get(session_id)
        base_session = baseline_sessions.get(session_id)

        if not isinstance(run_session, dict):
            diffs.append(
                ComparisonDiff(
                    session_id=session_id,
                    checkpoint_id="(session)",
                    severity="blocker",
                    code="session_missing_in_run",
                    message=f"Session '{session_id}' missing in run payload.",
                )
            )
            continue

        if not bool(run_session.get("passed", False)):
            diffs.append(
                ComparisonDiff(
                    session_id=session_id,
                    checkpoint_id="(session)",
                    severity="blocker",
                    code="session_failed",
                    message=f"Session '{session_id}' failed in current run.",
                )
            )

        run_checkpoints = run_session.get("checkpoints", {})
        if not isinstance(run_checkpoints, dict):
            run_checkpoints = {}
        run_expected = set(str(item).strip() for item in run_session.get("expected_checkpoints", []) if str(item).strip())
        for checkpoint_id in sorted(run_expected):
            if checkpoint_id in run_checkpoints:
                continue
            diffs.append(
                ComparisonDiff(
                    session_id=session_id,
                    checkpoint_id=checkpoint_id,
                    severity="blocker",
                    code="run_checkpoint_missing",
                    message=f"Required checkpoint '{checkpoint_id}' missing in run session '{session_id}'.",
                )
            )

        run_event_types = set(str(item).strip() for item in run_session.get("event_types", []) if str(item).strip())
        run_event_count = int(run_session.get("event_count", 0))
        if run_event_count <= 0:
            diffs.append(
                ComparisonDiff(
                    session_id=session_id,
                    checkpoint_id="(session)",
                    severity="major",
                    code="run_events_missing",
                    message=f"Session '{session_id}' has no recorded interaction events.",
                )
            )

        if not isinstance(base_session, dict):
            diffs.append(
                ComparisonDiff(
                    session_id=session_id,
                    checkpoint_id="(session)",
                    severity="major",
                    code="baseline_session_missing",
                    message=f"Session '{session_id}' has no baseline entry.",
                )
            )
            for checkpoint_id, run_cp in run_checkpoints.items():
                if not isinstance(run_cp, dict):
                    continue
                run_snapshot = run_cp.get("snapshot", {})
                if isinstance(run_snapshot, dict):
                    diffs.extend(
                        _ensure_checkpoint_shape(
                            session_id=session_id,
                            checkpoint_id=checkpoint_id,
                            snapshot=run_snapshot,
                        )
                    )
            continue

        base_checkpoints = base_session.get("checkpoints", {})
        if not isinstance(base_checkpoints, dict):
            base_checkpoints = {}

        base_expected = set(str(item).strip() for item in base_session.get("expected_checkpoints", []) if str(item).strip())
        for checkpoint_id in sorted(base_expected):
            if checkpoint_id in run_checkpoints:
                continue
            diffs.append(
                ComparisonDiff(
                    session_id=session_id,
                    checkpoint_id=checkpoint_id,
                    severity="blocker",
                    code="baseline_required_checkpoint_missing",
                    message=f"Checkpoint '{checkpoint_id}' expected by baseline but missing in run.",
                )
            )

        base_event_types = set(str(item).strip() for item in base_session.get("event_types", []) if str(item).strip())
        missing_event_types = sorted(base_event_types - run_event_types)
        if missing_event_types:
            diffs.append(
                ComparisonDiff(
                    session_id=session_id,
                    checkpoint_id="(session)",
                    severity="major",
                    code="event_types_missing",
                    message=f"Run session '{session_id}' missing baseline event types: {', '.join(missing_event_types)}.",
                )
            )
        base_event_count = int(base_session.get("event_count", 0))
        if run_event_count < max(1, int(base_event_count * 0.6)):
            diffs.append(
                ComparisonDiff(
                    session_id=session_id,
                    checkpoint_id="(session)",
                    severity="minor",
                    code="event_count_regression",
                    message=(
                        f"Run session '{session_id}' event_count={run_event_count} is below "
                        f"baseline threshold derived from {base_event_count}."
                    ),
                )
            )

        for checkpoint_id, base_cp in base_checkpoints.items():
            if not isinstance(base_cp, dict):
                continue
            run_cp = run_checkpoints.get(checkpoint_id)
            if not isinstance(run_cp, dict):
                diffs.append(
                    ComparisonDiff(
                        session_id=session_id,
                        checkpoint_id=checkpoint_id,
                        severity="major",
                        code="baseline_checkpoint_missing_in_run",
                        message=f"Checkpoint '{checkpoint_id}' missing in run for session '{session_id}'.",
                    )
                )
                continue
            run_snapshot = run_cp.get("snapshot", {})
            base_snapshot = base_cp.get("snapshot", {})
            if not isinstance(run_snapshot, dict) or not isinstance(base_snapshot, dict):
                diffs.append(
                    ComparisonDiff(
                        session_id=session_id,
                        checkpoint_id=checkpoint_id,
                        severity="major",
                        code="snapshot_shape_invalid",
                        message=f"Checkpoint '{checkpoint_id}' snapshot shape invalid.",
                    )
                )
                continue
            diffs.extend(
                _ensure_checkpoint_shape(
                    session_id=session_id,
                    checkpoint_id=checkpoint_id,
                    snapshot=run_snapshot,
                )
            )
            for key in (
                "active_tab_id",
                "selected_entry_id",
                "picker_open",
                "inspector_visible",
            ):
                if run_snapshot.get(key) == base_snapshot.get(key):
                    continue
                diffs.append(
                    ComparisonDiff(
                        session_id=session_id,
                        checkpoint_id=checkpoint_id,
                        severity="major",
                        code="semantic_state_mismatch",
                        message=f"Checkpoint '{checkpoint_id}' key '{key}' differs from baseline.",
                    )
                )
            diffs.extend(
                _compare_geometry(
                    session_id=session_id,
                    checkpoint_id=checkpoint_id,
                    base_snapshot=base_snapshot,
                    run_snapshot=run_snapshot,
                )
            )

    covered_capabilities = {
        int(item)
        for item in run_payload.get("covered_capabilities", [])
        if str(item).strip().isdigit()
    }
    for capability_id in sorted(set(int(item) for item in (required_capabilities or []) if str(item).strip().isdigit())):
        if capability_id in covered_capabilities:
            continue
        severity = "blocker" if capability_id <= 40 else "major"
        diffs.append(
            ComparisonDiff(
                session_id="(capabilities)",
                checkpoint_id="(coverage)",
                severity=severity,
                code="required_capability_uncovered",
                message=f"Required capability {capability_id} has no passing session evidence in this run.",
            )
        )

    max_severity = _severity_max(diffs)
    counts_by_severity = {
        severity: sum(1 for item in diffs if item.severity == severity)
        for severity in ("blocker", "major", "minor", "informational")
    }
    return {
        "passed": not any(item.severity in {"blocker", "major"} for item in diffs),
        "max_severity": max_severity,
        "diff_count": len(diffs),
        "counts_by_severity": counts_by_severity,
        "diffs": [item.to_payload() for item in diffs],
    }
