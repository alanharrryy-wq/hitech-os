#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
from pathlib import Path
from typing import Any

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.reports import timestamp_slug, write_json_report
from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.stable_json import dump_json
from tools.hos.hygiene.scan_large_files import scan_large_files
from tools.hos.hygiene.scan_root_artifacts import scan_root_artifacts
from tools.hos.hygiene.scan_worktree_contamination import scan_worktree_contamination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Optional hygiene scanner bundle.")
    parser.add_argument("--include-large-files", action="store_true", help="Include large file scanner.")
    parser.add_argument("--large-file-min-mb", type=float, default=10.0, help="Threshold for large file scan.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when root/worktree issues exist.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    root_payload = scan_root_artifacts(repo_root=repo_root)
    worktree_payload = scan_worktree_contamination(repo_root=repo_root)
    large_payload: dict[str, Any] | None = None
    if args.include_large_files:
        threshold = max(1, int(args.large_file_min_mb * 1024 * 1024))
        large_payload = scan_large_files(repo_root=repo_root, min_bytes=threshold, limit=200)

    issues = 0
    if not root_payload["ok"]:
        issues += 1
    if not worktree_payload.get("ok", True):
        issues += 1

    payload: dict[str, Any] = {
        "ok": issues == 0,
        "issues": issues,
        "strict": args.strict,
        "checks": {
            "rootArtifacts": root_payload,
            "worktreeContamination": worktree_payload,
            "largeFiles": large_payload,
        },
    }

    report_name = f"hygiene_{timestamp_slug()}.json"
    report_path = write_json_report(
        repo_root=repo_root,
        file_name=report_name,
        payload=payload,
        local=True,
        subdir="hygiene",
    )

    if args.json:
        print(dump_json(payload), end="")
    else:
        print(f"[cli_hygiene] ok={payload['ok']} issues={payload['issues']} strict={args.strict}")
        print(f"[cli_hygiene] report={report_path.as_posix()}")

    if args.strict and issues > 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
