
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path

from lib.common import discover_repo_root, stable_json_dumps
from lib.coordination import coordination_plane_root, ensure_round_context_exists, write_coordination_event
from lib.heartbeats import build_heartbeat_message


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit a validated chat heartbeat into the coordination plane.")
    parser.add_argument("--run-id", required=True, help="Run identifier under ops/runs.")
    parser.add_argument("--round-id", required=True, help="Round identifier under the selected run.")
    parser.add_argument("--chat-id", required=True, help="Registered chat identifier from chat_topology.json.")
    parser.add_argument("--status", required=True, choices=["planned", "in_progress", "blocked", "done"], help="Current chat status.")
    parser.add_argument("--status-summary", required=True, help="Human-readable summary of current state.")
    parser.add_argument("--current-item-ref", action="append", default=[], help="Repo-relative item currently being worked. Repeat for multiple items.")
    parser.add_argument("--next-planned-action", default="", help="Immediate next action expected from this chat.")
    parser.add_argument("--tag", action="append", default=[], help="Optional tag. Repeat for multiple tags.")
    parser.add_argument("--last-progress-at-utc", default="", help="Optional UTC timestamp of the last material progress event.")
    parser.add_argument("--message-id", default="", help="Optional deterministic message identifier.")
    parser.add_argument("--published-at-utc", default="", help="Optional UTC timestamp. Defaults to now.")
    args = parser.parse_args()

    repo_root = discover_repo_root(Path(__file__).resolve())
    ensure_round_context_exists(repo_root, args.run_id, args.round_id)
    plane_root = coordination_plane_root(repo_root, args.run_id, args.round_id)
    if not plane_root.exists():
        raise SystemExit(
            f"Coordination plane does not exist for run '{args.run_id}' round '{args.round_id}'. "
            "Run init_coordination_plane.py first."
        )

    message = build_heartbeat_message(
        repo_root=repo_root,
        run_id=args.run_id,
        round_id=args.round_id,
        chat_id=args.chat_id,
        status=args.status,
        status_summary=args.status_summary,
        current_item_refs=args.current_item_ref,
        next_planned_action=args.next_planned_action or None,
        tags=args.tag,
        last_progress_at_utc=args.last_progress_at_utc or None,
        message_id=args.message_id or None,
        published_at_utc=args.published_at_utc or None,
    )
    target = write_coordination_event(repo_root, args.run_id, args.round_id, message)
    result = {
        "status": "written",
        "path": str(target),
        "message": message,
    }
    print(stable_json_dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
