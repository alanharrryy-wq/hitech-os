from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from typing import Any

from lib.common import discover_repo_root, stable_json_dumps, utc_now, read_json, write_json
from lib.config import load_system_config


def _safe_read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = read_json(path)
    return payload if isinstance(payload, dict) else None


def _round_metrics(round_root: Path, system: dict[str, Any]) -> dict[str, Any]:
    reports_dir = round_root / system["reports_dir_name"]
    incoming_dir = round_root / system["incoming_dir_name"]
    acceptance = _safe_read_json(reports_dir / "acceptance_report.json") or {}
    overlap = _safe_read_json(reports_dir / "overlap_report.json") or {}

    package_results = acceptance.get("package_results", [])
    accepted = sum(1 for item in package_results if isinstance(item, dict) and item.get("status") in {"accept", "accept_with_conditions"})
    rejected = sum(1 for item in package_results if isinstance(item, dict) and item.get("status") == "reject")
    waivers_dir = reports_dir / "waivers"
    waiver_files = sorted(waivers_dir.glob("*.json")) if waivers_dir.exists() else []
    waiver_decisions = []
    for path in waiver_files:
        payload = _safe_read_json(path) or {}
        waiver_decisions.append(str(payload.get("decision_status", "unknown")).lower())
    approved_waivers = sum(1 for value in waiver_decisions if value == "approved")

    return {
        "round_id": round_root.name,
        "overall_status": acceptance.get("overall_status", "unknown"),
        "incoming_bundle_count": len(list(incoming_dir.glob("*.zip"))) if incoming_dir.exists() else 0,
        "accepted_packages": accepted,
        "rejected_packages": rejected,
        "conflict_count": len(overlap.get("conflicts", [])) if isinstance(overlap.get("conflicts"), list) else 0,
        "waiver_count": len(waiver_files),
        "approved_waiver_count": approved_waivers,
    }


def _build_alerts(round_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    for row in round_rows:
        if row["rejected_packages"] > 0 or row["overall_status"] == "reject":
            alerts.append({"severity": "high", "round_id": row["round_id"], "message": "round has rejected package bundles"})
        if row["conflict_count"] > 0:
            alerts.append({"severity": "high", "round_id": row["round_id"], "message": "round has unresolved overlap conflicts"})
        if row["waiver_count"] > 0 and row["approved_waiver_count"] < row["waiver_count"]:
            alerts.append({"severity": "medium", "round_id": row["round_id"], "message": "round has waiver artifacts without approved decision_status"})
    return alerts


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit run-level observability metrics and alert signals.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", help="Optional explicit output path")
    args = parser.parse_args()

    repo_root = discover_repo_root(Path(__file__).resolve())
    system = load_system_config(repo_root)
    run_root = repo_root / system["runs_root"] / args.run_id
    rounds_root = run_root / system["rounds_dir_name"]
    if not run_root.exists():
        print(stable_json_dumps({"ok": False, "error": f"run does not exist: {run_root}"}))
        return 1

    round_rows = []
    if rounds_root.exists():
        for round_dir in sorted(path for path in rounds_root.iterdir() if path.is_dir()):
            round_rows.append(_round_metrics(round_dir, system))

    alerts = _build_alerts(round_rows)
    report = {
        "schema_version": "1.0",
        "generated_at_utc": utc_now(),
        "run_id": args.run_id,
        "round_count": len(round_rows),
        "rounds": round_rows,
        "alerts": alerts,
        "ok": len([a for a in alerts if a["severity"] == "high"]) == 0,
    }

    output_path = Path(args.output) if args.output else run_root / system["reports_dir_name"] / "run_observability_metrics.json"
    write_json(output_path, report)
    print(stable_json_dumps({"ok": True, "output_path": str(output_path), "high_alerts": len([a for a in alerts if a['severity'] == 'high'])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
