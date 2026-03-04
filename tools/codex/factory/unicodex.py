from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Mapping

from .common import CODEX_DIR, INTEGRATOR, RUNS_DIR, WORKERS, ensure_dir, iso_utc, read_json, write_json
from .ledger import read_events

STATE_DIR = CODEX_DIR / "_state"
STATE_PATH = STATE_DIR / "UNICODEX_MODE.json"
PENDING_PATH = STATE_DIR / "UNICODEX_PENDING.json"

TERMINAL_STATUSES = {"PASS", "BLOCKED", "FAIL", "WARN", "OK"}


def _default_state() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "enabled": False,
        "mode": "MULTICODEX",
        "updated_at": "",
        "source": "",
        "deferred_from_run_id": "",
        "notes": "",
    }


def _default_pending() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "status": "NONE",
        "requested_at": "",
        "requested_by": "",
        "reason": "",
        "defer_until_run_id": "",
        "applied_at": "",
        "cancelled_at": "",
    }


def _read_mapping(path: Path, defaults: Mapping[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = dict(defaults)
    if not path.exists():
        return payload
    try:
        loaded = read_json(path)
    except Exception:
        return payload
    if not isinstance(loaded, Mapping):
        return payload
    for key, value in loaded.items():
        payload[str(key)] = value
    return payload


def _write_mapping(path: Path, payload: Mapping[str, Any]) -> None:
    ensure_dir(path.parent)
    write_json(path, dict(payload))


def _normalize_status(value: Any) -> str:
    text = str(value or "").strip().upper()
    return text or "PENDING"


def _iso_from_timestamp(timestamp: float) -> str:
    return dt.datetime.fromtimestamp(float(timestamp), tz=dt.timezone.utc).replace(microsecond=0).isoformat()


def _run_manifest(run_id: str) -> dict[str, Any]:
    manifest_path = RUNS_DIR / run_id / "RUN_MANIFEST.json"
    if not manifest_path.exists():
        return {}
    try:
        payload = read_json(manifest_path)
    except Exception:
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _workers_for_run(run_id: str) -> list[str]:
    manifest = _run_manifest(run_id)
    for key in ("ordered_workers", "workers"):
        raw_workers = manifest.get(key)
        if not isinstance(raw_workers, list):
            continue
        parsed = [
            str(item).strip()
            for item in raw_workers
            if str(item).strip() and str(item).strip() not in {INTEGRATOR, "Z_integrator"}
        ]
        if parsed:
            return parsed
    return list(WORKERS)


def _bundle_status(run_id: str, worker: str) -> str:
    path = RUNS_DIR / run_id / worker / "STATUS.json"
    if not path.exists():
        return "PENDING"
    try:
        payload = read_json(path)
    except Exception:
        return "PENDING"
    if not isinstance(payload, Mapping):
        return "PENDING"
    return _normalize_status(payload.get("status", "PENDING"))


def _ledger_state() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    try:
        events = read_events(strict=False)
    except Exception:
        return rows
    for event in events:
        run_id = str(event.get("run_id", "")).strip()
        if not run_id:
            continue
        row = rows.setdefault(run_id, {"has_run_end": False, "last_event": "", "last_ts_utc": ""})
        row["last_event"] = str(event.get("event_type", "")).strip().upper()
        row["last_ts_utc"] = str(event.get("ts_utc", "")).strip()
        if row["last_event"] == "RUN_END":
            row["has_run_end"] = True
    return rows


def inspect_run_completion(run_id: str, *, ledger_state: Mapping[str, Mapping[str, Any]] | None = None) -> dict[str, Any]:
    run_key = str(run_id).strip()
    run_dir = RUNS_DIR / run_key
    workers = _workers_for_run(run_key)
    worker_statuses = {worker: _bundle_status(run_key, worker) for worker in workers}
    non_terminal_workers = sorted(
        worker for worker, status in worker_statuses.items() if _normalize_status(status) not in TERMINAL_STATUSES
    )
    z_status = _bundle_status(run_key, INTEGRATOR)
    ledger_view = dict((ledger_state or _ledger_state()).get(run_key, {}))
    has_run_end = bool(ledger_view.get("has_run_end", False))
    last_event = str(ledger_view.get("last_event", "")).strip().upper()
    complete = bool(
        run_dir.exists()
        and (
            has_run_end
            or (_normalize_status(z_status) in TERMINAL_STATUSES and not non_terminal_workers)
        )
    )
    return {
        "run_id": run_key,
        "run_exists": run_dir.exists(),
        "run_dir": run_dir.as_posix(),
        "workers_total": len(workers),
        "worker_statuses": worker_statuses,
        "non_terminal_workers": non_terminal_workers,
        "integrator_status": z_status,
        "has_run_end_event": has_run_end,
        "last_ledger_event": last_event,
        "complete": complete,
    }


def _factory_run_dirs() -> list[Path]:
    if not RUNS_DIR.exists():
        return []
    runs: list[Path] = []
    for item in RUNS_DIR.iterdir():
        if not item.is_dir():
            continue
        manifest = _run_manifest(item.name)
        if manifest:
            if str(manifest.get("kind", "")).strip().lower() != "factory":
                continue
        elif not item.name.startswith("factory"):
            continue
        runs.append(item)
    runs.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return runs


def list_active_runs(*, limit: int = 5) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ledger_state = _ledger_state()
    for run_dir in _factory_run_dirs():
        probe = inspect_run_completion(run_dir.name, ledger_state=ledger_state)
        if probe["complete"]:
            continue
        row = {
            "run_id": run_dir.name,
            "run_dir": run_dir.as_posix(),
            "last_modified_utc": _iso_from_timestamp(run_dir.stat().st_mtime),
            "workers_total": probe["workers_total"],
            "non_terminal_workers": list(probe["non_terminal_workers"]),
            "integrator_status": str(probe["integrator_status"]),
            "has_run_end_event": bool(probe.get("has_run_end_event", False)),
            "last_ledger_event": str(probe.get("last_ledger_event", "")),
        }
        rows.append(row)
        if len(rows) >= max(1, int(limit)):
            break
    return rows


def read_unicodex_state() -> dict[str, Any]:
    return _read_mapping(STATE_PATH, _default_state())


def read_unicodex_pending() -> dict[str, Any]:
    return _read_mapping(PENDING_PATH, _default_pending())


def _set_state(*, enabled: bool, source: str, deferred_from_run_id: str = "", notes: str = "") -> dict[str, Any]:
    state = read_unicodex_state()
    state["enabled"] = bool(enabled)
    state["mode"] = "UNICODEX" if enabled else "MULTICODEX"
    state["updated_at"] = iso_utc()
    state["source"] = str(source)
    state["deferred_from_run_id"] = str(deferred_from_run_id or "")
    if notes:
        state["notes"] = str(notes)
    _write_mapping(STATE_PATH, state)
    return state


def _set_pending(payload: Mapping[str, Any]) -> dict[str, Any]:
    pending = _default_pending()
    for key, value in dict(payload).items():
        pending[str(key)] = value
    _write_mapping(PENDING_PATH, pending)
    return pending


def enable_unicodex(
    *,
    defer_until_run_id: str | None = None,
    reason: str = "operator_request",
    requested_by: str = "operator",
    force_now: bool = False,
) -> dict[str, Any]:
    requested_run = str(defer_until_run_id or "").strip()
    chosen_run = requested_run
    if not chosen_run and not force_now:
        active = list_active_runs(limit=1)
        if active:
            chosen_run = str(active[0]["run_id"])
    if chosen_run and not force_now:
        probe = inspect_run_completion(chosen_run)
        if not probe["complete"]:
            pending = _set_pending(
                {
                    "schema_version": 1,
                    "status": "PENDING",
                    "requested_at": iso_utc(),
                    "requested_by": str(requested_by),
                    "reason": str(reason),
                    "defer_until_run_id": chosen_run,
                    "applied_at": "",
                    "cancelled_at": "",
                }
            )
            return {
                "status": "PASS",
                "action": "enable",
                "activation": "DEFERRED",
                "detail": "UNICODEX deferred until run completion",
                "target_run": probe,
                "state": read_unicodex_state(),
                "pending": pending,
                "active_runs": list_active_runs(limit=5),
                "state_path": STATE_PATH.as_posix(),
                "pending_path": PENDING_PATH.as_posix(),
            }

    state = _set_state(
        enabled=True,
        source=f"unicodex.enable:{reason}",
        deferred_from_run_id=chosen_run,
        notes="enabled without run_id requirement and with global governance authority",
    )
    pending = _set_pending(_default_pending())
    return {
        "status": "PASS",
        "action": "enable",
        "activation": "IMMEDIATE",
        "detail": "UNICODEX enabled immediately",
        "state": state,
        "pending": pending,
        "active_runs": list_active_runs(limit=5),
        "state_path": STATE_PATH.as_posix(),
        "pending_path": PENDING_PATH.as_posix(),
    }


def disable_unicodex(*, clear_pending: bool = True, reason: str = "operator_request") -> dict[str, Any]:
    state = _set_state(enabled=False, source=f"unicodex.disable:{reason}", deferred_from_run_id="", notes="")
    pending = read_unicodex_pending()
    if clear_pending:
        if _normalize_status(pending.get("status")) == "PENDING":
            pending["status"] = "CANCELLED"
            pending["cancelled_at"] = iso_utc()
            pending["applied_at"] = ""
            _write_mapping(PENDING_PATH, pending)
        else:
            pending = _set_pending(_default_pending())
    return {
        "status": "PASS",
        "action": "disable",
        "detail": "UNICODEX disabled",
        "state": state,
        "pending": pending,
        "active_runs": list_active_runs(limit=5),
        "state_path": STATE_PATH.as_posix(),
        "pending_path": PENDING_PATH.as_posix(),
    }


def reconcile_unicodex(*, run_id: str | None = None) -> dict[str, Any]:
    pending = read_unicodex_pending()
    pending_status = _normalize_status(pending.get("status"))
    if pending_status != "PENDING":
        return {
            "status": "PASS",
            "action": "reconcile",
            "applied": False,
            "detail": "no pending UNICODEX activation",
            "state": read_unicodex_state(),
            "pending": pending,
            "active_runs": list_active_runs(limit=5),
            "state_path": STATE_PATH.as_posix(),
            "pending_path": PENDING_PATH.as_posix(),
        }

    target_run_id = str(pending.get("defer_until_run_id", "")).strip()
    trigger_run_id = str(run_id or "").strip()
    if target_run_id and trigger_run_id and trigger_run_id != target_run_id:
        return {
            "status": "PASS",
            "action": "reconcile",
            "applied": False,
            "detail": f"pending activation waits for run_id={target_run_id}",
            "state": read_unicodex_state(),
            "pending": pending,
            "active_runs": list_active_runs(limit=5),
            "state_path": STATE_PATH.as_posix(),
            "pending_path": PENDING_PATH.as_posix(),
        }

    target_probe = inspect_run_completion(target_run_id) if target_run_id else {}
    if target_run_id and not target_probe.get("complete", False):
        return {
            "status": "PASS",
            "action": "reconcile",
            "applied": False,
            "detail": "target run is not complete yet",
            "target_run": target_probe,
            "state": read_unicodex_state(),
            "pending": pending,
            "active_runs": list_active_runs(limit=5),
            "state_path": STATE_PATH.as_posix(),
            "pending_path": PENDING_PATH.as_posix(),
        }

    state = _set_state(
        enabled=True,
        source="unicodex.reconcile:deferred_activation",
        deferred_from_run_id=target_run_id,
        notes="deferred activation promoted after worker and integrator completion",
    )
    pending["status"] = "APPLIED"
    pending["applied_at"] = iso_utc()
    pending["cancelled_at"] = ""
    _write_mapping(PENDING_PATH, pending)
    return {
        "status": "PASS",
        "action": "reconcile",
        "applied": True,
        "detail": "UNICODEX activation applied after run completion",
        "target_run": target_probe,
        "state": state,
        "pending": pending,
        "active_runs": list_active_runs(limit=5),
        "state_path": STATE_PATH.as_posix(),
        "pending_path": PENDING_PATH.as_posix(),
    }


def status_unicodex(*, run_id: str | None = None) -> dict[str, Any]:
    pending = read_unicodex_pending()
    state = read_unicodex_state()
    probe_run = str(run_id or "").strip() or str(pending.get("defer_until_run_id", "")).strip()
    probe = inspect_run_completion(probe_run) if probe_run else {}
    return {
        "status": "PASS",
        "action": "status",
        "state": state,
        "pending": pending,
        "active_runs": list_active_runs(limit=5),
        "probe": probe,
        "state_path": STATE_PATH.as_posix(),
        "pending_path": PENDING_PATH.as_posix(),
    }
