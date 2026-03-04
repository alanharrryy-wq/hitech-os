#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
MEMORY_DIR = REPO_ROOT / "tools" / "codex" / "memory"
RUNS_DIR = REPO_ROOT / "tools" / "codex" / "runs"


def _iso_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _ensure_memory_files() -> dict[str, Path]:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    files = {
        "run_history": MEMORY_DIR / "RUN_HISTORY.json",
        "tech_debt": MEMORY_DIR / "TECH_DEBT.json",
        "fail_patterns": MEMORY_DIR / "FAIL_PATTERNS.json",
        "success_patterns": MEMORY_DIR / "SUCCESS_PATTERNS.json",
    }

    defaults = {
        "run_history": {"schema_version": 1, "updated_at_utc": _iso_utc(), "runs": []},
        "tech_debt": {"schema_version": 1, "updated_at_utc": _iso_utc(), "items": []},
        "fail_patterns": {"schema_version": 1, "updated_at_utc": _iso_utc(), "patterns": []},
        "success_patterns": {"schema_version": 1, "updated_at_utc": _iso_utc(), "patterns": []},
    }

    for key, path in files.items():
        if not path.exists():
            _write_json(path, defaults[key])
    return files


def _load_run_snapshot(run_id: str) -> dict[str, Any]:
    run_root = RUNS_DIR / run_id
    manifest = _read_json(run_root / "RUN_MANIFEST.json", {})
    z_status = _read_json(run_root / "Z_integrator" / "STATUS.json", {})
    z_report = run_root / "Z_integrator" / "FINAL_REPORT.txt"
    return {
        "run_id": run_id,
        "run_root": run_root.as_posix(),
        "manifest": manifest if isinstance(manifest, dict) else {},
        "z_status": z_status if isinstance(z_status, dict) else {},
        "report_path": z_report.as_posix(),
        "report_exists": z_report.exists(),
    }


def _upsert_run_history(path: Path, snapshot: dict[str, Any]) -> None:
    payload = _read_json(path, {"schema_version": 1, "runs": []})
    runs = payload.get("runs", []) if isinstance(payload.get("runs", []), list) else []
    run_id = str(snapshot.get("run_id", "")).strip()
    status = str(snapshot.get("z_status", {}).get("status", "PENDING")).upper()
    row = {
        "run_id": run_id,
        "recorded_at_utc": _iso_utc(),
        "status": status,
        "kind": str(snapshot.get("manifest", {}).get("kind", "factory")),
        "base_ref": str(snapshot.get("manifest", {}).get("base_ref", "HEAD")),
        "workers": snapshot.get("manifest", {}).get("workers", []),
        "report_path": str(snapshot.get("report_path", "")),
        "anti_padding_blockers": int(snapshot.get("z_status", {}).get("anti_padding_blockers", 0) or 0),
        "blockers": snapshot.get("z_status", {}).get("blockers", []),
    }

    replaced = False
    for idx, existing in enumerate(runs):
        if isinstance(existing, dict) and str(existing.get("run_id", "")).strip() == run_id:
            runs[idx] = row
            replaced = True
            break
    if not replaced:
        runs.append(row)

    payload["schema_version"] = 1
    payload["updated_at_utc"] = _iso_utc()
    payload["runs"] = sorted(
        [item for item in runs if isinstance(item, dict)],
        key=lambda item: str(item.get("run_id", "")),
    )
    _write_json(path, payload)


def _update_patterns(path: Path, *, key: str, title: str, evidence: str, run_id: str) -> None:
    payload = _read_json(path, {"schema_version": 1, "patterns": []})
    patterns = payload.get("patterns", []) if isinstance(payload.get("patterns", []), list) else []

    found = False
    for row in patterns:
        if not isinstance(row, dict):
            continue
        if str(row.get("key", "")).strip() == key:
            row["count"] = int(row.get("count", 0) or 0) + 1
            row["last_seen_run_id"] = run_id
            row["last_seen_utc"] = _iso_utc()
            row.setdefault("examples", [])
            examples = row.get("examples", []) if isinstance(row.get("examples", []), list) else []
            if evidence and evidence not in examples:
                examples.append(evidence)
            row["examples"] = examples[-5:]
            found = True
            break

    if not found:
        patterns.append(
            {
                "key": key,
                "title": title,
                "count": 1,
                "first_seen_utc": _iso_utc(),
                "last_seen_utc": _iso_utc(),
                "last_seen_run_id": run_id,
                "examples": [evidence] if evidence else [],
            }
        )

    payload["schema_version"] = 1
    payload["updated_at_utc"] = _iso_utc()
    payload["patterns"] = sorted(
        [item for item in patterns if isinstance(item, dict)],
        key=lambda item: (str(item.get("key", "")), str(item.get("title", ""))),
    )
    _write_json(path, payload)


def _append_tech_debt(path: Path, *, run_id: str, blockers: list[str]) -> None:
    payload = _read_json(path, {"schema_version": 1, "items": []})
    items = payload.get("items", []) if isinstance(payload.get("items", []), list) else []

    for blocker in blockers:
        text = str(blocker).strip()
        if not text:
            continue
        key = f"{run_id}:{text}"
        if any(isinstance(item, dict) and str(item.get("key", "")) == key for item in items):
            continue
        items.append(
            {
                "key": key,
                "run_id": run_id,
                "created_at_utc": _iso_utc(),
                "severity": "medium",
                "owner": "factory",
                "title": text[:160],
                "status": "open",
            }
        )

    payload["schema_version"] = 1
    payload["updated_at_utc"] = _iso_utc()
    payload["items"] = sorted(
        [item for item in items if isinstance(item, dict)],
        key=lambda item: str(item.get("key", "")),
    )
    _write_json(path, payload)


def record_run(run_id: str) -> dict[str, Any]:
    files = _ensure_memory_files()
    snapshot = _load_run_snapshot(run_id)
    z_status = snapshot.get("z_status", {}) if isinstance(snapshot.get("z_status", {}), dict) else {}
    status = str(z_status.get("status", "PENDING")).upper()
    blockers = [str(item) for item in (z_status.get("blockers", []) if isinstance(z_status.get("blockers", []), list) else []) if str(item).strip()]

    _upsert_run_history(files["run_history"], snapshot)

    if status in {"BLOCKED", "FAIL"}:
        title = "Factory run blocked"
        evidence = blockers[0] if blockers else "blocked without explicit blocker"
        _update_patterns(files["fail_patterns"], key="factory_run_blocked", title=title, evidence=evidence, run_id=run_id)
        _append_tech_debt(files["tech_debt"], run_id=run_id, blockers=blockers)
    elif status == "PASS":
        _update_patterns(
            files["success_patterns"],
            key="factory_run_pass",
            title="Factory run pass",
            evidence=f"report={snapshot.get('report_path','')}",
            run_id=run_id,
        )

    return {
        "status": "PASS",
        "run_id": run_id,
        "memory_dir": MEMORY_DIR.as_posix(),
        "files": {key: value.as_posix() for key, value in files.items()},
        "recorded_status": status,
        "blockers_count": len(blockers),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex memory layer manager")
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("init", help="Create memory layer files if missing")
    init_cmd.set_defaults(func=lambda _args: {"status": "PASS", "files": {k: v.as_posix() for k, v in _ensure_memory_files().items()}})

    record_cmd = sub.add_parser("record-run", help="Record run summary and pattern updates")
    record_cmd.add_argument("--run-id", required=True)
    record_cmd.set_defaults(func=lambda args: record_run(str(args.run_id).strip()))

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = args.func(args)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if str(payload.get("status", "PASS")).upper() == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
