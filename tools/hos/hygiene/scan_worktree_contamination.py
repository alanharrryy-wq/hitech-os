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

from tools.hos._core.exec import run_command
from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.stable_json import dump_json


def scan_worktree_contamination(repo_root: Path) -> dict[str, Any]:
    target = "tools/codex/worktrees"
    result = run_command(["git", "status", "--porcelain", "--", target], cwd=repo_root, check=False)
    if result.classification == "not_found":
        return {
            "ok": True,
            "supported": False,
            "reason": "git_not_found",
            "entries": [],
        }

    entries = []
    for raw in result.stdout.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        status = line[:2].strip()
        path = line[3:].strip() if len(line) > 3 else ""
        entries.append({"status": status, "path": path})

    entries.sort(key=lambda item: (item["path"], item["status"]))
    return {
        "ok": len(entries) == 0,
        "supported": True,
        "entries": entries,
        "entryCount": len(entries),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect accidental changes in tools/codex/worktrees.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    payload = scan_worktree_contamination(repo_root=repo_root)
    if args.json:
        print(dump_json(payload), end="")
    else:
        print(f"[scan_worktree_contamination] ok={payload.get('ok')} entries={payload.get('entryCount', 0)}")
        for entry in payload.get("entries", []):
            print(f" - {entry['status']} {entry['path']}")
    return 0 if payload.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
