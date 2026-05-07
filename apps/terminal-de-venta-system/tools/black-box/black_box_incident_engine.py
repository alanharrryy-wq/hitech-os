#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRISMA black-box i02 R5 Incident Engine.

This module is intentionally import-light and side-effect-light until a command is
executed. It owns local black-box incident records only. It does not touch Tablet,
PC, Mobile, DB, schema, contracts, or shared-kernel files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ENGINE_ID = "black_box_i02_r5_incident_engine"
ENGINE_VERSION = "0.1.0"

STATE_READY = "READY"
STATE_READY_WITH_CAVEATS = "READY_WITH_CAVEATS"
STATE_BLOCKED = "BLOCKED"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def stamp() -> str:
    return utc_now().strftime("%Y%m%d_%H%M%S_UTC")


def iso_now() -> str:
    return utc_now().isoformat()


def resolve_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def ensure_layout(out_root: Path) -> Dict[str, Path]:
    layout = {
        "root": out_root,
        "incidents": out_root / "incidents",
        "active": out_root / "incidents" / "active",
        "resolved": out_root / "incidents" / "resolved",
        "archived": out_root / "incidents" / "archived",
        "runtime": out_root / "runtime",
        "reports": out_root / "reports",
        "evidence": out_root / "evidence",
        "logs": out_root / "logs",
    }
    for path in layout.values():
        path.mkdir(parents=True, exist_ok=True)
    return layout


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def append_jsonl(path: Path, event: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    value = value.lower().strip()
    value = re.sub(r"\d{4}-\d{2}-\d{2}[t ][0-9:.+\-z]+", "<time>", value)
    value = re.sub(r"\b\d+ms\b", "<ms>", value)
    value = re.sub(r"\b\d+\b", "<n>", value)
    value = re.sub(r"\s+", " ", value)
    return value[:300]


def parse_checks(checks_line: str) -> Dict[str, int]:
    result = {"OK": 0, "WARN": 0, "FAIL": 0, "ACTIVE_HITS": 0, "RESOLVED_HITS": 0}
    for key in result:
        match = re.search(rf"{re.escape(key)}=(\d+)", checks_line or "")
        if match:
            result[key] = int(match.group(1))
    return result


def parse_status_stdout(stdout: str) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {
        "headline": "",
        "state": "UNKNOWN",
        "root": "",
        "active_root_cause": "",
        "primary_caveat": "",
        "checks": "",
        "checks_parsed": parse_checks(""),
        "report": "",
    }
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("PRISMA BLACK-BOX"):
            parsed["headline"] = line
            if ":" in line:
                parsed["state"] = line.rsplit(":", 1)[-1].strip()
        elif line.startswith("Root:"):
            parsed["root"] = line.split(":", 1)[1].strip()
        elif line.startswith("Active root cause:"):
            parsed["active_root_cause"] = line.split(":", 1)[1].strip()
        elif line.startswith("Primary caveat:"):
            parsed["primary_caveat"] = line.split(":", 1)[1].strip()
        elif line.startswith("Checks:"):
            parsed["checks"] = line.split(":", 1)[1].strip()
            parsed["checks_parsed"] = parse_checks(parsed["checks"])
        elif line.startswith("Report:"):
            parsed["report"] = line.split(":", 1)[1].strip()
    return parsed


def run_command(label: str, command: List[str], cwd: Path, evidence_dir: Path, env_extra: Optional[Dict[str, str]] = None, timeout_sec: int = 60) -> Dict[str, Any]:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    start = time.time()
    record: Dict[str, Any] = {
        "label": label,
        "command": command,
        "cwd": str(cwd),
        "started_at": iso_now(),
    }
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
        )
        record.update({
            "returncode": proc.returncode,
            "elapsed_ms": int((time.time() - start) * 1000),
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "timed_out": False,
        })
    except subprocess.TimeoutExpired as exc:
        record.update({
            "returncode": 124,
            "elapsed_ms": int((time.time() - start) * 1000),
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
        })
    write_json(evidence_dir / f"{label}.json", record)
    return record


def status_command(target_root: Path, out_root: Path) -> Tuple[List[str], Path]:
    black_box = target_root / "tools" / "black-box" / "black_box.py"
    return [
        sys.executable,
        str(black_box),
        "status",
        "--root",
        str(target_root),
        "--out",
        str(out_root),
        "--allow-blocked",
    ], target_root


def determine_incident(parsed: Dict[str, Any], command_record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    checks = parsed.get("checks_parsed") or {}
    state = parsed.get("state") or "UNKNOWN"
    root_cause = parsed.get("active_root_cause") or ""
    caveat = parsed.get("primary_caveat") or ""
    rc = command_record.get("returncode", 1)

    if rc != 0:
        severity = "FAIL"
        family = "black_box_status_command"
        title = "black_box.py status returned non-zero"
        active_reason = f"returncode={rc}"
    elif state == STATE_BLOCKED:
        severity = "FAIL"
        family = "black_box_blocked"
        title = "Black-box status is BLOCKED"
        active_reason = root_cause or "BLOCKED"
    elif checks.get("FAIL", 0) > 0 or checks.get("ACTIVE_HITS", 0) > 0:
        severity = "FAIL"
        family = "black_box_active_failure"
        title = "Black-box active failure detected"
        active_reason = f"checks={parsed.get('checks', '')} root_cause={root_cause}"
    elif state == STATE_READY_WITH_CAVEATS and caveat:
        severity = "WARN"
        family = "black_box_caveat"
        title = "Black-box caveat detected"
        active_reason = caveat
    elif "NO_ACTIVE_FAILURE" not in root_cause and root_cause:
        severity = "WARN"
        family = "black_box_root_cause_noncanonical"
        title = "Black-box root cause is not NO_ACTIVE_FAILURE"
        active_reason = root_cause
    else:
        return None

    normalized = {
        "family": family,
        "state": state,
        "root_cause": normalize_text(root_cause),
        "caveat": normalize_text(caveat),
        "checks": parsed.get("checks", ""),
        "returncode": rc,
    }
    raw = json.dumps(normalized, sort_keys=True, ensure_ascii=False)
    fingerprint = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    incident_id = f"INC_{fingerprint}"
    return {
        "id": incident_id,
        "fingerprint": fingerprint,
        "family": family,
        "title": title,
        "severity": severity,
        "status": "active",
        "active_reason": active_reason,
        "state": state,
        "root_cause": root_cause,
        "primary_caveat": caveat,
        "checks": parsed.get("checks", ""),
        "normalized": normalized,
        "first_seen_at": iso_now(),
        "last_seen_at": iso_now(),
        "source": ENGINE_ID,
    }


def incident_summary_md(incident: Dict[str, Any]) -> str:
    lines = [
        f"# PRISMA black-box incident {incident.get('id')}",
        "",
        f"- status: {incident.get('status')}",
        f"- severity: {incident.get('severity')}",
        f"- family: {incident.get('family')}",
        f"- title: {incident.get('title')}",
        f"- first_seen_at: {incident.get('first_seen_at')}",
        f"- last_seen_at: {incident.get('last_seen_at')}",
        f"- active_reason: {incident.get('active_reason')}",
        f"- state: {incident.get('state')}",
        f"- root_cause: {incident.get('root_cause')}",
        f"- primary_caveat: {incident.get('primary_caveat')}",
        f"- checks: {incident.get('checks')}",
        "",
        "## Notes",
        "",
        "This incident is managed by black_box_i02_r5_incident_engine. It is deduped by fingerprint.",
    ]
    return "\n".join(lines) + "\n"


def write_or_update_incident(out_root: Path, incident: Dict[str, Any], evidence_dir: Path, status_record: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
    layout = ensure_layout(out_root)
    active_dir = layout["active"] / incident["id"]
    active_dir.mkdir(parents=True, exist_ok=True)
    incident_path = active_dir / "incident.json"
    previous = read_json(incident_path, {})
    now = iso_now()
    if previous:
        incident["first_seen_at"] = previous.get("first_seen_at", incident["first_seen_at"])
        incident["occurrences"] = int(previous.get("occurrences", 0)) + 1
    else:
        incident["occurrences"] = 1
    incident["last_seen_at"] = now
    incident["evidence_dir"] = str(evidence_dir)
    incident["status_record"] = str(evidence_dir / "black_box_status.json")
    incident["parsed_status_record"] = str(evidence_dir / "black_box_status_parsed.json")
    write_json(incident_path, incident)
    (active_dir / "summary.md").write_text(incident_summary_md(incident), encoding="utf-8")
    append_jsonl(active_dir / "timeline.jsonl", {
        "ts": now,
        "event": "seen",
        "severity": incident.get("severity"),
        "state": incident.get("state"),
        "checks": incident.get("checks"),
        "primary_caveat": incident.get("primary_caveat"),
        "root_cause": incident.get("root_cause"),
        "evidence_dir": str(evidence_dir),
    })
    evidence_copy_dir = active_dir / "evidence"
    evidence_copy_dir.mkdir(parents=True, exist_ok=True)
    for src_name in ["black_box_status.json", "black_box_status_parsed.json"]:
        src = evidence_dir / src_name
        if src.exists():
            shutil.copy2(src, evidence_copy_dir / f"{stamp()}_{src_name}")
    return incident


def list_active_incidents(out_root: Path) -> List[Dict[str, Any]]:
    layout = ensure_layout(out_root)
    incidents = []
    for path in sorted(layout["active"].glob("INC_*/incident.json")):
        data = read_json(path, None)
        if isinstance(data, dict):
            incidents.append(data)
    return incidents


def list_resolved_incidents(out_root: Path) -> List[Dict[str, Any]]:
    layout = ensure_layout(out_root)
    incidents = []
    for path in sorted(layout["resolved"].glob("INC_*/incident.json")):
        data = read_json(path, None)
        if isinstance(data, dict):
            incidents.append(data)
    return incidents


def update_index(out_root: Path, last: Optional[Dict[str, Any]], state: str, report: Optional[Path]) -> Dict[str, Any]:
    layout = ensure_layout(out_root)
    active = list_active_incidents(out_root)
    resolved = list_resolved_incidents(out_root)
    index = {
        "engine": ENGINE_ID,
        "version": ENGINE_VERSION,
        "updated_at": iso_now(),
        "state": state,
        "active_count": len(active),
        "resolved_count": len(resolved),
        "active_ids": [item.get("id") for item in active],
        "last_incident_id": last.get("id") if last else None,
        "last_report": str(report) if report else None,
    }
    write_json(layout["runtime"] / "incident_index.json", index)
    write_json(layout["runtime"] / "last_incident.json", last or {
        "engine": ENGINE_ID,
        "updated_at": iso_now(),
        "status": "none",
        "message": "No active incident detected in latest scan.",
    })
    return index


def auto_resolve_own_active(out_root: Path, reason: str, evidence_dir: Path) -> List[str]:
    layout = ensure_layout(out_root)
    resolved_ids: List[str] = []
    for inc_json in sorted(layout["active"].glob("INC_*/incident.json")):
        incident = read_json(inc_json, {})
        if incident.get("source") != ENGINE_ID:
            continue
        incident["status"] = "resolved"
        incident["resolved_at"] = iso_now()
        incident["resolution_reason"] = reason
        incident["resolution_evidence_dir"] = str(evidence_dir)
        src_dir = inc_json.parent
        dst_dir = layout["resolved"] / src_dir.name
        if dst_dir.exists():
            dst_dir = layout["resolved"] / f"{src_dir.name}_{stamp()}"
        write_json(inc_json, incident)
        append_jsonl(src_dir / "timeline.jsonl", {
            "ts": iso_now(),
            "event": "resolved",
            "reason": reason,
            "evidence_dir": str(evidence_dir),
        })
        shutil.move(str(src_dir), str(dst_dir))
        resolved_ids.append(incident.get("id", dst_dir.name))
    return resolved_ids


def write_scan_report(out_root: Path, state: str, parsed: Dict[str, Any], command_record: Dict[str, Any], incident: Optional[Dict[str, Any]], index: Dict[str, Any], evidence_dir: Path, resolved_ids: List[str]) -> Tuple[Path, Path]:
    layout = ensure_layout(out_root)
    ts = stamp()
    json_path = layout["reports"] / f"black_box_i02_r5_incident_engine_scan_{ts}.json"
    md_path = layout["reports"] / f"black_box_i02_r5_incident_engine_scan_{ts}.md"
    payload = {
        "engine": ENGINE_ID,
        "version": ENGINE_VERSION,
        "created_at": iso_now(),
        "state": state,
        "parsed_status": parsed,
        "black_box_status": command_record,
        "incident": incident,
        "incident_index": index,
        "resolved_ids": resolved_ids,
        "evidence_dir": str(evidence_dir),
    }
    write_json(json_path, payload)
    lines = [
        "# PRISMA black-box i02 R5 Incident Engine scan",
        "",
        f"Generated: {payload['created_at']}",
        f"State: {state}",
        "",
        "## Parsed black-box status",
        "",
        f"- headline: {parsed.get('headline')}",
        f"- root cause: {parsed.get('active_root_cause')}",
        f"- caveat: {parsed.get('primary_caveat')}",
        f"- checks: {parsed.get('checks')}",
        f"- report: {parsed.get('report')}",
        "",
        "## Incident",
        "",
    ]
    if incident:
        lines.extend([
            f"- id: {incident.get('id')}",
            f"- severity: {incident.get('severity')}",
            f"- status: {incident.get('status')}",
            f"- occurrences: {incident.get('occurrences')}",
            f"- active_reason: {incident.get('active_reason')}",
        ])
    else:
        lines.append("- No active incident detected.")
    if resolved_ids:
        lines.extend(["", "## Auto-resolved", ""])
        for item in resolved_ids:
            lines.append(f"- {item}")
    lines.extend(["", "## Evidence", "", f"- evidence_dir: `{evidence_dir}`", f"- json: `{json_path}`"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def cmd_scan(args: argparse.Namespace) -> int:
    target_root = resolve_path(args.root)
    out_root = resolve_path(args.out)
    layout = ensure_layout(out_root)
    evidence_dir = layout["evidence"] / f"black_box_i02_r5_incident_engine_{stamp()}"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    black_box = target_root / "tools" / "black-box" / "black_box.py"
    blockers: List[str] = []
    if not target_root.exists():
        blockers.append(f"target root missing: {target_root}")
    if not black_box.exists():
        blockers.append(f"black_box.py missing: {black_box}")
    if blockers:
        payload = {"state": STATE_BLOCKED, "blockers": blockers, "created_at": iso_now()}
        write_json(evidence_dir / "preflight_blocked.json", payload)
        print(f"PRISMA BLACK-BOX i02 R5 INCIDENT ENGINE: {STATE_BLOCKED}")
        for blocker in blockers:
            print(f"Blocker: {blocker}")
        return 2

    command, cwd = status_command(target_root, out_root)
    record = run_command("black_box_status", command, cwd, evidence_dir, env_extra={"PRISMA_BB_I02_R5_ROUTER_BYPASS": "1"}, timeout_sec=args.timeout_sec)
    parsed = parse_status_stdout(record.get("stdout", ""))
    write_json(evidence_dir / "black_box_status_parsed.json", parsed)

    incident = determine_incident(parsed, record)
    resolved_ids: List[str] = []
    state = parsed.get("state") or STATE_READY
    if incident:
        incident = write_or_update_incident(out_root, incident, evidence_dir, record, parsed)
        state = STATE_BLOCKED if incident.get("severity") == "FAIL" and parsed.get("state") == STATE_BLOCKED else STATE_READY_WITH_CAVEATS
    else:
        if args.auto_resolve:
            resolved_ids = auto_resolve_own_active(out_root, "latest scan has no active incident signature", evidence_dir)
        state = STATE_READY

    index = update_index(out_root, incident, state, None)
    report_json, report_md = write_scan_report(out_root, state, parsed, record, incident, index, evidence_dir, resolved_ids)
    index["last_report"] = str(report_md)
    update_index(out_root, incident, state, report_md)
    write_json(layout["runtime"] / "incident_engine_latest.json", {
        "engine": ENGINE_ID,
        "version": ENGINE_VERSION,
        "state": state,
        "updated_at": iso_now(),
        "report_json": str(report_json),
        "report_md": str(report_md),
        "evidence_dir": str(evidence_dir),
    })

    print(f"PRISMA BLACK-BOX i02 R5 INCIDENT ENGINE: {state}")
    print(f"Active incidents: {len(list_active_incidents(out_root))}")
    if incident:
        print(f"Last incident: {incident.get('id')} ({incident.get('severity')})")
    else:
        print("Last incident: none")
    if resolved_ids:
        print("Auto-resolved: " + ", ".join(resolved_ids))
    print(f"Report: {report_md}")
    print(f"Evidence: {evidence_dir}")
    return 0 if state in {STATE_READY, STATE_READY_WITH_CAVEATS} else 2


def cmd_list(args: argparse.Namespace) -> int:
    out_root = resolve_path(args.out)
    ensure_layout(out_root)
    active = list_active_incidents(out_root)
    resolved = list_resolved_incidents(out_root)
    selected: List[Dict[str, Any]]
    if args.state == "active":
        selected = active
    elif args.state == "resolved":
        selected = resolved
    else:
        selected = active + resolved
    print(f"PRISMA BLACK-BOX i02 R5 INCIDENTS: {len(selected)} shown")
    for item in selected:
        print(f"{item.get('id')} | {item.get('status')} | {item.get('severity')} | {item.get('title')} | last={item.get('last_seen_at')}")
    return 0


def cmd_last(args: argparse.Namespace) -> int:
    out_root = resolve_path(args.out)
    layout = ensure_layout(out_root)
    last = read_json(layout["runtime"] / "last_incident.json", {})
    print(json.dumps(last, indent=2, ensure_ascii=False))
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    out_root = resolve_path(args.out)
    layout = ensure_layout(out_root)
    inc_id = args.id
    active_dir = layout["active"] / inc_id
    inc_json = active_dir / "incident.json"
    if not inc_json.exists():
        print(f"Incident not active or not found: {inc_id}", file=sys.stderr)
        return 2
    incident = read_json(inc_json, {})
    incident["status"] = "resolved"
    incident["resolved_at"] = iso_now()
    incident["resolution_reason"] = args.reason
    write_json(inc_json, incident)
    append_jsonl(active_dir / "timeline.jsonl", {"ts": iso_now(), "event": "manual_resolve", "reason": args.reason})
    dst_dir = layout["resolved"] / active_dir.name
    if dst_dir.exists():
        dst_dir = layout["resolved"] / f"{active_dir.name}_{stamp()}"
    shutil.move(str(active_dir), str(dst_dir))
    update_index(out_root, incident, STATE_READY_WITH_CAVEATS, None)
    print(f"Resolved incident: {inc_id}")
    print(f"Resolved path: {dst_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="black_box.py incidents", description="PRISMA black-box i02 R5 incident engine")
    sub = parser.add_subparsers(dest="command")

    scan = sub.add_parser("scan", help="Run black-box status, dedupe incident fingerprint, and write timeline/evidence")
    scan.add_argument("--root", required=True, help="Terminal de Venta target root")
    scan.add_argument("--out", required=True, help="Black-box output root")
    scan.add_argument("--allow-blocked", action="store_true", help="Accepted for command compatibility")
    scan.add_argument("--timeout-sec", type=int, default=90)
    scan.add_argument("--no-auto-resolve", dest="auto_resolve", action="store_false")
    scan.set_defaults(func=cmd_scan, auto_resolve=True)

    list_cmd = sub.add_parser("list", help="List active/resolved incidents")
    list_cmd.add_argument("--out", required=True, help="Black-box output root")
    list_cmd.add_argument("--state", choices=["active", "resolved", "all"], default="active")
    list_cmd.set_defaults(func=cmd_list)

    last = sub.add_parser("last", help="Print runtime last_incident.json")
    last.add_argument("--out", required=True, help="Black-box output root")
    last.set_defaults(func=cmd_last)

    resolve = sub.add_parser("resolve", help="Manually resolve an active incident")
    resolve.add_argument("--out", required=True, help="Black-box output root")
    resolve.add_argument("--id", required=True, help="Incident id, for example INC_abc123")
    resolve.add_argument("--reason", default="manual resolution")
    resolve.set_defaults(func=cmd_resolve)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in {"incidents", "incident"}:
        argv = argv[1:]
    if not argv:
        argv = ["scan"]
    if argv[0] == "status":
        argv[0] = "scan"
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
