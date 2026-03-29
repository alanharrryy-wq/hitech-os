
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path
from typing import Any

from lib.blockers import summarize_blockers
from lib.common import SCHEMA_VERSION, discover_repo_root, stable_json_dumps, utc_now, write_json, write_text
from lib.coordination import (
    compute_global_status,
    coordination_channel_dir,
    coordination_plane_root,
    coordination_snapshots_dir,
    ensure_round_context_exists,
    latest_message_by_chat,
    load_channel_events,
    load_coordination_configs,
    normalize_message_event,
    parse_utc,
    read_json,
    render_markdown_table,
    summarize_checkpoint_events,
)
from lib.handoffs import normalize_handoff_ticket, summarize_handoffs
from lib.heartbeats import summarize_heartbeats


def _load_json_files(directory: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not directory.exists():
        return [], []
    items: list[dict[str, Any]] = []
    issues: list[str] = []
    for path in sorted(directory.glob("*.json")):
        try:
            items.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as exc:
            issues.append(f"{path.name}: invalid JSON ({exc.msg})")
    return items, issues


def _load_handoff_tickets(repo_root: Path, run_id: str, round_id: str) -> tuple[list[dict[str, Any]], list[str]]:
    channel_dir = coordination_channel_dir(repo_root, run_id, round_id, "channel.handoffs")
    raw_items, issues = _load_json_files(channel_dir)
    tickets: list[dict[str, Any]] = []
    for index, payload in enumerate(raw_items):
        try:
            if "handoff_id" not in payload:
                raise ValueError("handoff channel entries must include handoff_id")
            tickets.append(normalize_handoff_ticket(payload, repo_root))
        except ValueError as exc:
            issues.append(f"{channel_dir.name}[{index}]: {exc}")
    return tickets, issues


def _merge_window_readiness(
    package_map: list[dict[str, Any]],
    checkpoint_summary: dict[str, Any],
    blocker_summary: dict[str, Any],
    handoff_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    latest_checkpoints = checkpoint_summary.get("latest_by_chat", {})
    blocker_rows = blocker_summary.get("rows", [])
    handoff_rows = handoff_summary.get("rows", [])
    rows: list[dict[str, Any]] = []
    for item in package_map:
        package_id = item["package_id"]
        chat_id = item["chat_id"]
        checkpoint = latest_checkpoints.get(chat_id, {})
        open_blockers = [row for row in blocker_rows if row.get("package_id") == package_id]
        open_handoffs = [row for row in handoff_rows if row.get("package_id") == package_id and row.get("status") != "done"]
        evidence_count = 0
        if checkpoint:
            evidence_count = len(checkpoint.get("evidence_refs", []))
        ready = bool(checkpoint) and checkpoint.get("status") == "done" and not open_blockers and not open_handoffs
        rows.append({
            "package_id": package_id,
            "chat_id": chat_id,
            "checkpoint_status": checkpoint.get("status", ""),
            "open_blocker_count": len(open_blockers),
            "open_handoff_count": len(open_handoffs),
            "evidence_refs_count": evidence_count,
            "ready_for_integration": ready,
            "latest_snapshot_ref": "coordination_snapshot.latest.json",
        })
    return rows


def _build_markdown(
    snapshot: dict[str, Any],
    heartbeat_summary: dict[str, Any],
    checkpoint_summary: dict[str, Any],
    handoff_summary: dict[str, Any],
    blocker_summary: dict[str, Any],
    merge_rows: list[dict[str, Any]],
) -> str:
    lines = [
        f"# Coordination Snapshot {snapshot['snapshot_id']}",
        "",
        f"- Generated at: {snapshot['generated_at_utc']}",
        f"- Run: {snapshot['run_id']}",
        f"- Round: {snapshot['round_id']}",
        f"- Global status: {snapshot['global_status']['status']}",
        "",
        "## Global reasons",
    ]
    reasons = snapshot["global_status"].get("reasons", [])
    if reasons:
        lines.extend([f"- {reason}" for reason in reasons])
    else:
        lines.append("- No exceptional coordination risks detected.")
    lines.extend([
        "",
        "## Coordination overview",
        "",
        render_markdown_table(
            heartbeat_summary["rows"],
            [
                "chat_id",
                "heartbeat_status",
                "silence_state",
                "heartbeat_age_minutes",
                "status_summary",
                "next_planned_action",
            ],
        ).rstrip(),
        "",
        "## Latest checkpoints",
        "",
        render_markdown_table(
            checkpoint_summary["rows"],
            ["chat_id", "status", "package_id", "published_at_utc", "status_summary", "next_planned_action"],
        ).rstrip(),
        "",
        "## Handoff queue",
        "",
        render_markdown_table(
            handoff_summary["rows"],
            [
                "handoff_id",
                "from_chat_id",
                "to_chat_id",
                "status",
                "severity",
                "ack_state",
                "resolution_state",
                "requested_outcome",
            ],
        ).rstrip(),
        "",
        "## Blocker pressure",
        "",
        render_markdown_table(
            blocker_summary["rows"],
            [
                "blocker_id",
                "severity",
                "blocker_type",
                "owner_chat_id",
                "package_id",
                "age_minutes",
                "next_action_owner",
            ],
        ).rstrip(),
        "",
        "## Merge window readiness",
        "",
        render_markdown_table(
            merge_rows,
            [
                "package_id",
                "chat_id",
                "checkpoint_status",
                "open_blocker_count",
                "open_handoff_count",
                "ready_for_integration",
            ],
        ).rstrip(),
        "",
    ])
    issues = snapshot.get("issues", [])
    if issues:
        lines.extend(["## Data issues", ""])
        lines.extend([f"- {issue}" for issue in issues])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate coordination heartbeats, handoffs, blockers, and checkpoints into a stable snapshot.")
    parser.add_argument("--run-id", required=True, help="Run identifier under ops/runs.")
    parser.add_argument("--round-id", required=True, help="Round identifier under the selected run.")
    parser.add_argument("--snapshot-id", default="", help="Optional deterministic snapshot identifier.")
    parser.add_argument("--output-json", default="", help="Optional explicit JSON output path.")
    parser.add_argument("--output-markdown", default="", help="Optional explicit markdown output path.")
    args = parser.parse_args()

    repo_root = discover_repo_root(Path(__file__).resolve())
    ensure_round_context_exists(repo_root, args.run_id, args.round_id)
    plane_root = coordination_plane_root(repo_root, args.run_id, args.round_id)
    if not plane_root.exists():
        raise SystemExit(
            f"Coordination plane does not exist for run '{args.run_id}' round '{args.round_id}'. "
            "Run init_coordination_plane.py first."
        )

    configs = load_coordination_configs(repo_root)
    manifest_path = plane_root / "coordination_plane_manifest.json"
    initialized_at_utc = ""
    if manifest_path.exists():
        initialized_at_utc = read_json(manifest_path).get("initialized_at_utc", "")

    heartbeat_events, heartbeat_issues = load_channel_events(repo_root, args.run_id, args.round_id, "channel.heartbeats")
    checkpoint_events, checkpoint_issues = load_channel_events(repo_root, args.run_id, args.round_id, "channel.sync_checkpoints")
    blocker_events, blocker_issues = load_channel_events(repo_root, args.run_id, args.round_id, "channel.blockers")
    handoff_tickets, handoff_issues = _load_handoff_tickets(repo_root, args.run_id, args.round_id)

    generated_at_utc = utc_now()
    heartbeat_summary = summarize_heartbeats(
        repo_root,
        heartbeat_events,
        now_utc=generated_at_utc,
        initialized_at_utc=initialized_at_utc or None,
    )
    checkpoint_summary = summarize_checkpoint_events(checkpoint_events)
    handoff_summary = summarize_handoffs(repo_root, handoff_tickets, now_utc=generated_at_utc)
    blocker_summary = summarize_blockers(repo_root, blocker_events, now_utc=generated_at_utc)
    merge_rows = _merge_window_readiness(
        configs["operator_dashboard_views"].get("package_map", []),
        checkpoint_summary,
        blocker_summary,
        handoff_summary,
    )

    snapshot_id = args.snapshot_id or f"coordination-snapshot-{parse_utc(generated_at_utc).strftime('%Y%m%dT%H%M%SZ')}"
    issues = heartbeat_issues + checkpoint_issues + blocker_issues + handoff_issues
    global_status = compute_global_status(heartbeat_summary, checkpoint_summary, handoff_summary, blocker_summary)
    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "snapshot_id": snapshot_id,
        "generated_at_utc": generated_at_utc,
        "run_id": args.run_id,
        "round_id": args.round_id,
        "global_status": global_status,
        "counts": {
            "heartbeats": heartbeat_summary["counts"],
            "checkpoints": checkpoint_summary["counts"],
            "handoffs": handoff_summary["counts"],
            "blockers": blocker_summary["counts"],
        },
        "views": {
            "coordination_overview": heartbeat_summary["rows"],
            "latest_checkpoints": checkpoint_summary["rows"],
            "handoff_queue": handoff_summary["rows"],
            "blocker_pressure": blocker_summary["rows"],
            "merge_window_readiness": merge_rows,
        },
        "issues": issues,
    }

    markdown = _build_markdown(snapshot, heartbeat_summary, checkpoint_summary, handoff_summary, blocker_summary, merge_rows)
    snapshots_dir = coordination_snapshots_dir(repo_root, args.run_id, args.round_id)
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    latest_json_path = snapshots_dir / "coordination_snapshot.latest.json"
    latest_markdown_path = snapshots_dir / "coordination_snapshot.latest.md"
    write_json(latest_json_path, snapshot)
    write_text(latest_markdown_path, markdown)

    timestamp_json_path = snapshots_dir / f"{snapshot_id}.json"
    timestamp_markdown_path = snapshots_dir / f"{snapshot_id}.md"
    write_json(timestamp_json_path, snapshot)
    write_text(timestamp_markdown_path, markdown)

    if args.output_json:
        write_json(Path(args.output_json), snapshot)
    if args.output_markdown:
        write_text(Path(args.output_markdown), markdown)

    result = {
        "status": "written",
        "snapshot_json": str(latest_json_path),
        "snapshot_markdown": str(latest_markdown_path),
        "snapshot_id": snapshot_id,
        "global_status": global_status,
        "issues": issues,
    }
    print(stable_json_dumps(result))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
