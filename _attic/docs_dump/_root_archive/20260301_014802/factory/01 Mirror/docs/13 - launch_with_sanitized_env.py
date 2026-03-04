from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from factory.worktree_contract import FIXED_WORKTREE_MODE, resolve_unified_worktree_mode
else:
    from .worktree_contract import FIXED_WORKTREE_MODE, resolve_unified_worktree_mode


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run factory launch with sanitized env for unified fixed worktrees")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workers", required=True)
    parser.add_argument("--base-ref", default="HEAD")
    parser.add_argument("--config", default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        mode_info = resolve_unified_worktree_mode()
    except ValueError as exc:
        _emit(
            {
                "status": "BLOCKED",
                "run_id": args.run_id,
                "error": str(exc),
            }
        )
        return 2

    if str(mode_info.get("worktree_mode", "")).strip().lower() != FIXED_WORKTREE_MODE:
        _emit(
            {
                "status": "BLOCKED",
                "run_id": args.run_id,
                "error": f"unsupported worktree_mode in unified launcher: {mode_info.get('worktree_mode', '')!r}",
            }
        )
        return 2

    env_copy = dict(os.environ)
    env_copy.pop("FACTORY_AHK_EXE", None)
    env_copy["FACTORY_WORKTREE_MODE"] = FIXED_WORKTREE_MODE

    cmd = [
        sys.executable,
        "-m",
        "tools.codex.factory",
        "launch",
        "--run-id",
        str(args.run_id),
        "--workers",
        str(args.workers),
        "--base-ref",
        str(args.base_ref),
    ]
    if args.config:
        cmd.extend(["--config", str(args.config)])
    if args.dry_run:
        cmd.append("--dry-run")

    proc = subprocess.run(
        cmd,
        cwd=str(Path(__file__).resolve().parents[3]),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env_copy,
        check=False,
    )

    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
