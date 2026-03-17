from __future__ import annotations

import hashlib
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Mapping

from .common import INTEGRATOR, RUNS_DIR, ensure_dir, iso_utc
from .schemas import validate_payload
from .status_eval import BLOCKED, PASS, status_exit_code

LEDGER_PATH = RUNS_DIR / "factory_ledger.jsonl"
LEDGER_SIGNATURE_PATH = RUNS_DIR / "factory_ledger.sha256"
LEDGER_LOCK_PATH = RUNS_DIR / "factory_ledger.lock"
EVENT_TYPES = {
    "RUN_START",
    "RUN_INIT",
    "PREFLIGHT",
    "WORKTREE_CREATE",
    "LAUNCH_RESULT",
    "WORKER_BUNDLE_DISCOVERED",
    "BUNDLE_VALIDATED",
    "OVERLAP_CHECK",
    "SCOPE_CHECK",
    "INTEGRATE_START",
    "REPORT_WRITTEN",
    "INTEGRATION_RESULT",
    "RUN_END",
    "RUN_STATE",
    "ONESHOT_SUMMARY",
}


class CorruptLedgerError(ValueError):
    pass


def _default_event() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "ts_utc": iso_utc(),
        "run_id": "",
        "event_type": "RUN_STATE",
        "actor": "",
        "event_id": "",
        "parent_event_id": "",
        "duration_ms": 0,
        "file_counts": {},
        "hashes": {},
        "rc": 0,
        "details": {},
    }


def _normalize_event(event: Mapping[str, Any]) -> dict[str, Any]:
    payload = _default_event()
    payload.update(dict(event))

    payload["schema_version"] = int(payload.get("schema_version", 1))
    payload["ts_utc"] = str(payload.get("ts_utc", "") or iso_utc())
    payload["run_id"] = str(payload.get("run_id", "")).strip()
    payload["event_type"] = str(payload.get("event_type", "RUN_STATE")).strip().upper()
    payload["actor"] = str(payload.get("actor", "")).strip()
    payload["parent_event_id"] = str(payload.get("parent_event_id", "") or "").strip()
    payload["duration_ms"] = max(0, int(payload.get("duration_ms", 0)))
    payload["rc"] = int(payload.get("rc", 0))

    hashes = payload.get("hashes", {})
    payload["hashes"] = dict(hashes) if isinstance(hashes, Mapping) else {}

    file_counts = payload.get("file_counts", {})
    payload["file_counts"] = dict(file_counts) if isinstance(file_counts, Mapping) else {}

    details = payload.get("details", {})
    payload["details"] = dict(details) if isinstance(details, Mapping) else {"value": details}

    event_id = str(payload.get("event_id", "")).strip()
    if not event_id:
        seed = json.dumps(
            {
                "run_id": payload["run_id"],
                "event_type": payload["event_type"],
                "actor": payload["actor"],
                "ts_utc": payload["ts_utc"],
                "details": payload["details"],
                "parent_event_id": payload["parent_event_id"],
            },
            sort_keys=True,
        )
        event_id = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    payload["event_id"] = event_id
    return payload


def _validate_event(event: Mapping[str, Any]) -> None:
    errors = validate_payload("run_ledger_event", dict(event))
    if errors:
        joined = "\n".join(errors)
        raise ValueError(f"ledger event payload invalid:\n{joined}")
    if str(event.get("event_type", "")) not in EVENT_TYPES:
        raise ValueError(f"ledger event_type not allowed: {event.get('event_type')!r}")


def _write_signature(ledger_path: Path, signature_path: Path) -> None:
    ensure_dir(signature_path.parent)
    if not ledger_path.exists():
        signature_path.write_text("", encoding="utf-8", newline="\n")
        return
    digest = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    signature_path.write_text(f"{digest}  {ledger_path.name}\n", encoding="utf-8", newline="\n")


@contextmanager
def _acquire_ledger_lock(lock_path: Path, *, timeout_seconds: float = 5.0):
    ensure_dir(lock_path.parent)
    start = time.monotonic()
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if (time.monotonic() - start) >= timeout_seconds:
                raise TimeoutError(f"ledger lock timeout: {lock_path.as_posix()}")
            time.sleep(0.05)
            continue
        try:
            os.write(fd, f"{os.getpid()} {iso_utc()}\n".encode("utf-8"))
        finally:
            os.close(fd)
        break
    try:
        yield
    finally:
        if lock_path.exists():
            lock_path.unlink()


def append_event(
    event: Mapping[str, Any],
    *,
    path: Path | None = None,
    signature_path: Path | None = None,
    lock_path: Path | None = None,
) -> dict[str, Any]:
    ledger_path = path or LEDGER_PATH
    sig_path = signature_path or LEDGER_SIGNATURE_PATH
    use_lock_path = lock_path or LEDGER_LOCK_PATH
    payload = _normalize_event(event)
    _validate_event(payload)

    with _acquire_ledger_lock(use_lock_path):
        ensure_dir(ledger_path.parent)
        with ledger_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
        _write_signature(ledger_path, sig_path)
    return payload


def read_events(*, path: Path | None = None, strict: bool = True) -> list[dict[str, Any]]:
    ledger_path = path or LEDGER_PATH
    if not ledger_path.exists():
        return []

    parsed: list[dict[str, Any]] = []
    with ledger_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            raw = line.strip()
            if not raw:
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as exc:
                if strict:
                    raise CorruptLedgerError(f"invalid ledger json at line {line_no}: {exc}") from exc
                continue
            if not isinstance(item, dict):
                if strict:
                    raise CorruptLedgerError(f"invalid ledger line #{line_no}: expected JSON object")
                continue
            payload = _normalize_event(item)
            try:
                _validate_event(payload)
            except ValueError as exc:
                if strict:
                    raise CorruptLedgerError(f"invalid ledger payload at line {line_no}: {exc}") from exc
                continue
            payload["_line"] = line_no
            parsed.append(payload)
    return parsed


def query_events(
    *,
    run_id: str | None = None,
    event_type: str | None = None,
    actor: str | None = None,
    rc: int | None = None,
    since: str | None = None,
    status: str | None = None,
    kind: str | None = None,
    limit: int = 50,
    path: Path | None = None,
) -> list[dict[str, Any]]:
    items = read_events(path=path)
    if run_id:
        items = [entry for entry in items if str(entry.get("run_id", "")) == run_id]
    if event_type:
        items = [entry for entry in items if str(entry.get("event_type", "")) == event_type]
    if actor:
        items = [entry for entry in items if str(entry.get("actor", "")) == actor]
    if rc is not None:
        items = [entry for entry in items if int(entry.get("rc", 0)) == int(rc)]
    if since:
        items = [entry for entry in items if str(entry.get("ts_utc", "")) >= since]
    if status:
        items = [entry for entry in items if str(entry.get("details", {}).get("status", "")) == status]
    if kind:
        items = [entry for entry in items if str(entry.get("details", {}).get("kind", "")) == kind]

    items.sort(
        key=lambda entry: (
            str(entry.get("ts_utc", "")),
            str(entry.get("event_type", "")),
            str(entry.get("run_id", "")),
            str(entry.get("actor", "")),
            int(entry.get("_line", 0)),
        )
    )
    cap = max(1, int(limit))
    return items[-cap:]


def query_run_ids(*, path: Path | None = None) -> list[str]:
    ids = sorted({str(entry.get("run_id", "")) for entry in read_events(path=path) if str(entry.get("run_id", ""))})
    return ids


def append_run(record: Mapping[str, Any], *, path: Path | None = None) -> dict[str, Any]:
    payload = dict(record)
    status = str(payload.get("status", "")).upper()
    rc = payload.get("rc")
    if rc is None:
        rc = status_exit_code(status if status else PASS)
    if status == BLOCKED and int(rc) == 0:
        rc = 2

    event = {
        "schema_version": 1,
        "ts_utc": str(payload.get("ts_utc", "") or iso_utc()),
        "run_id": str(payload.get("run_id", "")),
        "event_type": str(payload.get("event_type", "") or "RUN_STATE"),
        "actor": str(payload.get("actor", "") or INTEGRATOR),
        "event_id": str(payload.get("event_id", "") or ""),
        "parent_event_id": str(payload.get("parent_event_id", "") or ""),
        "duration_ms": int(payload.get("duration_ms", 0)),
        "file_counts": dict(payload.get("file_counts", {})) if isinstance(payload.get("file_counts"), Mapping) else {},
        "hashes": dict(payload.get("hashes", {})) if isinstance(payload.get("hashes"), Mapping) else {},
        "rc": int(rc),
        "details": payload,
    }
    return append_event(event, path=path)


def query_runs(
    *,
    status: str | None = None,
    kind: str | None = None,
    limit: int = 50,
    path: Path | None = None,
) -> list[dict[str, Any]]:
    events = query_events(status=status, kind=kind, limit=limit, path=path)
    output: list[dict[str, Any]] = []
    for entry in events:
        details = dict(entry.get("details", {}))
        details["ts_utc"] = entry.get("ts_utc", "")
        details["event_type"] = entry.get("event_type", "")
        details["actor"] = entry.get("actor", "")
        details["event_id"] = entry.get("event_id", "")
        details["parent_event_id"] = entry.get("parent_event_id", "")
        details["duration_ms"] = entry.get("duration_ms", 0)
        details["file_counts"] = entry.get("file_counts", {})
        details["rc"] = entry.get("rc", 0)
        details["hashes"] = entry.get("hashes", {})
        output.append(details)
    return output


def verify_ledger_signature(*, path: Path | None = None, signature_path: Path | None = None) -> dict[str, Any]:
    ledger_path = path or LEDGER_PATH
    sig_path = signature_path or LEDGER_SIGNATURE_PATH
    if not ledger_path.exists():
        return {"status": "BLOCKED", "detail": "ledger missing", "ledger": ledger_path.as_posix()}
    if not sig_path.exists():
        return {"status": "BLOCKED", "detail": "signature missing", "signature": sig_path.as_posix()}
    expected = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    line = sig_path.read_text(encoding="utf-8").strip()
    actual = line.split("  ", 1)[0] if line else ""
    return {
        "status": "PASS" if expected == actual else "BLOCKED",
        "expected": expected,
        "actual": actual,
        "ledger": ledger_path.as_posix(),
        "signature": sig_path.as_posix(),
    }


def replay_ledger(
    *,
    run_id: str | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    events = query_events(run_id=run_id, limit=1_000_000, path=path)
    runs: dict[str, dict[str, Any]] = {}
    for event in events:
        current_run_id = str(event.get("run_id", ""))
        state = runs.setdefault(
            current_run_id,
            {
                "run_id": current_run_id,
                "status": "UNKNOWN",
                "event_count": 0,
                "last_event_type": "",
                "last_event_id": "",
                "started_at": "",
                "ended_at": "",
                "actors": set(),
                "rc": 0,
            },
        )
        state["event_count"] += 1
        state["last_event_type"] = str(event.get("event_type", ""))
        state["last_event_id"] = str(event.get("event_id", ""))
        state["ended_at"] = str(event.get("ts_utc", ""))
        if not state["started_at"]:
            state["started_at"] = str(event.get("ts_utc", ""))
        details = event.get("details", {})
        if isinstance(details, Mapping) and details.get("status"):
            state["status"] = str(details.get("status"))
        state["actors"].add(str(event.get("actor", "")))
        state["rc"] = int(event.get("rc", 0))

    rows = []
    for run_key in sorted(runs):
        entry = dict(runs[run_key])
        entry["actors"] = sorted(actor for actor in entry["actors"] if actor)
        rows.append(entry)
    return {"status": "PASS", "runs": rows, "count": len(rows)}
