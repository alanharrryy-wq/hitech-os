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

from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.reports import timestamp_slug, write_json_report
from tools.hos._core.stable_json import dump_json
from tools.hos.visual.baseline_store import (
    resolve_baseline_paths,
    sync_captures_to_current,
    update_baselines,
)
from tools.hos.visual.compare import compare_directories
from tools.hos.visual.playwright_capture import capture_screenshots, parse_targets
from tools.hos.visual.storybook_detect import detect_storybook_workspaces
from tools.hos.visual.storybook_runner import start_storybook, stop_storybook


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic visual regression harness.")
    parser.add_argument("--suite", default="default", help="Baseline suite key.")
    parser.add_argument("--base-url", default="http://127.0.0.1:6007", help="Capture base URL.")
    parser.add_argument("--target", action="append", default=[], help="Target page in name=/path format.")
    parser.add_argument("--port", type=int, default=6007, help="Storybook port when auto-starting.")
    parser.add_argument("--start-storybook", action="store_true", help="Auto-start detected storybook.")
    parser.add_argument("--workspace", default="", help="Storybook workspace override.")
    parser.add_argument("--package-name", default="", help="Storybook package name override.")
    parser.add_argument("--threshold", type=float, default=0.0, help="Allowed visual diff ratio.")
    parser.add_argument("--update-baseline", action="store_true", help="Update tracked baselines from current captures.")
    parser.add_argument("--strict", action="store_true", help="Fail when capture cannot execute.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    return parser.parse_args()


def _select_storybook(repo_root: Path, workspace: str, package_name: str) -> tuple[str, str] | None:
    if workspace and package_name:
        return workspace, package_name
    matches = detect_storybook_workspaces(repo_root=repo_root)
    if not matches:
        return None
    first = matches[0]
    return first.workspace_path, first.package_name


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    paths = resolve_baseline_paths(repo_root=repo_root, suite=args.suite)

    runner = None
    storybook_info = None
    if args.start_storybook:
        storybook_info = _select_storybook(
            repo_root=repo_root,
            workspace=args.workspace,
            package_name=args.package_name,
        )
        if storybook_info is None:
            message = "[cli_visual] no storybook workspace detected."
            if args.strict:
                print(message)
                return 2
            print(message + " capture continues against provided --base-url.")
        else:
            workspace, package = storybook_info
            runner = start_storybook(
                repo_root=repo_root,
                workspace_name=workspace,
                package_name=package,
                port=args.port,
                timeout_seconds=75.0,
            )
            print(f"[cli_visual] storybook started workspace={workspace} package={package} port={args.port}")

    try:
        capture_root = (repo_root / "tools/_local/visual/capture" / args.suite / timestamp_slug()).resolve()
        targets = parse_targets(args.target) if args.target else [{"name": "root", "path": "/"}]
        capture = capture_screenshots(
            repo_root=repo_root,
            base_url=args.base_url,
            targets=targets,
            output_dir=capture_root,
        )
        if not capture.get("ok"):
            if args.strict:
                print("[cli_visual] capture failed in strict mode.")
                print(capture.get("stderr", "capture error"))
                return 2
            print("[cli_visual] capture failed but strict mode is off.")
            print(capture.get("stderr", capture.get("classification", "unknown failure")))
            payload: dict[str, Any] = {
                "ok": False,
                "capture": capture,
                "strict": args.strict,
            }
            if args.json:
                print(dump_json(payload), end="")
            report_name = f"visual_{timestamp_slug()}.json"
            write_json_report(repo_root=repo_root, file_name=report_name, payload=payload, local=True, subdir="visual")
            return 0

        copied = sync_captures_to_current(capture_root=capture_root, current_root=paths.current_dir)
        compare_payload = compare_directories(
            baseline_dir=paths.base_dir,
            current_dir=paths.current_dir,
            diff_dir=paths.diff_dir,
            threshold=max(0.0, min(1.0, args.threshold)),
        )
        updated: list[str] = []
        if args.update_baseline:
            updated_paths = update_baselines(current_root=paths.current_dir, baseline_root=paths.base_dir)
            updated = [item.as_posix() for item in updated_paths]

        payload = {
            "ok": compare_payload["failures"] == 0,
            "suite": args.suite,
            "captureCount": len(copied),
            "captureRoot": capture_root.as_posix(),
            "baselineDir": paths.base_dir.as_posix(),
            "currentDir": paths.current_dir.as_posix(),
            "diffDir": paths.diff_dir.as_posix(),
            "compare": compare_payload,
            "updatedBaselines": updated,
            "updateBaselineRequested": args.update_baseline,
            "strict": args.strict,
        }
        report_name = f"visual_{timestamp_slug()}.json"
        report_path = write_json_report(
            repo_root=repo_root,
            file_name=report_name,
            payload=payload,
            local=True,
            subdir="visual",
        )

        if args.json:
            print(dump_json(payload), end="")
        else:
            print(
                f"[cli_visual] suite={args.suite} captures={len(copied)} "
                f"failures={compare_payload['failures']} updated={len(updated)}"
            )
            print(f"[cli_visual] report={report_path.as_posix()}")
        return 0 if payload["ok"] else 1
    finally:
        if runner is not None:
            stop_storybook(runner.process)


if __name__ == "__main__":
    raise SystemExit(main())
