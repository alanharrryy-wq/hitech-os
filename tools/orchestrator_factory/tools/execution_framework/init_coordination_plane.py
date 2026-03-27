
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path

from lib.common import SCHEMA_VERSION, discover_repo_root, ensure_dir, read_json, stable_json_dumps, utc_now, write_json
from lib.coordination import (
    coordination_channel_dir,
    coordination_plane_root,
    coordination_round_root,
    coordination_snapshots_dir,
    coordination_views_dir,
    ensure_round_context_exists,
    load_coordination_configs,
)


def _ensure_json_file(path: Path, payload: dict) -> None:
    if path.exists():
        return
    write_json(path, payload)


def build_coordination_plane_manifest(repo_root: Path, run_id: str, round_id: str) -> dict:
    round_root = coordination_round_root(repo_root, run_id, round_id)
    round_manifest = read_json(round_root / "round_manifest.json")
    configs = load_coordination_configs(repo_root)
    topology = configs["chat_topology"]
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "round_id": round_id,
        "project_id": round_manifest.get("project_id", ""),
        "initialized_at_utc": utc_now(),
        "status": "ready",
        "coordination_root": str(coordination_plane_root(repo_root, run_id, round_id)),
        "channels": [item["channel_id"] for item in topology.get("channels", [])],
        "snapshot_files": {
            "latest_json": "snapshots/coordination_snapshot.latest.json",
            "latest_markdown": "snapshots/coordination_snapshot.latest.md",
        },
        "views_directory": "views",
        "notes": "Coordination plane bootstrap is idempotent and additive.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap the coordination plane for a run/round without modifying existing framework source files."
    )
    parser.add_argument("--run-id", required=True, help="Run identifier under ops/runs.")
    parser.add_argument("--round-id", required=True, help="Round identifier under the selected run.")
    args = parser.parse_args()

    repo_root = discover_repo_root(Path(__file__).resolve())
    ensure_round_context_exists(repo_root, args.run_id, args.round_id)
    plane_root = ensure_dir(coordination_plane_root(repo_root, args.run_id, args.round_id))
    channels_root = ensure_dir(plane_root / "channels")
    ensure_dir(coordination_snapshots_dir(repo_root, args.run_id, args.round_id))
    ensure_dir(coordination_views_dir(repo_root, args.run_id, args.round_id))

    topology = load_coordination_configs(repo_root)["chat_topology"]
    for channel in topology.get("channels", []):
        ensure_dir(coordination_channel_dir(repo_root, args.run_id, args.round_id, channel["channel_id"]))

    manifest_path = plane_root / "coordination_plane_manifest.json"
    _ensure_json_file(manifest_path, build_coordination_plane_manifest(repo_root, args.run_id, args.round_id))
    _ensure_json_file(
        plane_root / "views" / "dashboard_state.json",
        {
            "schema_version": SCHEMA_VERSION,
            "run_id": args.run_id,
            "round_id": args.round_id,
            "generated_at_utc": utc_now(),
            "available_views": [item["view_id"] for item in load_coordination_configs(repo_root)["operator_dashboard_views"].get("views", [])],
        },
    )

    result = {
        "schema_version": SCHEMA_VERSION,
        "run_id": args.run_id,
        "round_id": args.round_id,
        "coordination_root": str(plane_root),
        "channels_root": str(channels_root),
        "created_channels": sorted(item["channel_id"] for item in topology.get("channels", [])),
        "manifest_path": str(manifest_path),
        "status": "ready",
    }
    print(stable_json_dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
