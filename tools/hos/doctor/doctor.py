#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
import platform
import shutil
from pathlib import Path
from typing import Any

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.hashing import hash_directory
from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.reports import timestamp_slug, write_json_report
from tools.hos._core.stable_json import dump_json

REQUIRED_PATHS = (
    "tools/hos/_core",
    "tools/hos/turbo",
    "tools/hos/data",
    "tools/hos/visual",
    "tools/hos/ui",
    "tools/hos/hygiene",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Non-mutating doctor checks for HITECH toolchain.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


def command_available(command: str) -> bool:
    return shutil.which(command) is not None


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()

    command_matrix = {
        "python": command_available("python"),
        "node": command_available("node"),
        "pnpm": command_available("pnpm"),
        "turbo": command_available("turbo"),
        "git": command_available("git"),
    }
    path_matrix = {
        path: (repo_root / path).exists()
        for path in sorted(REQUIRED_PATHS)
    }
    missing_paths = sorted([path for path, exists in path_matrix.items() if not exists])
    missing_commands = sorted([name for name, exists in command_matrix.items() if not exists])

    payload: dict[str, Any] = {
        "ok": len(missing_paths) == 0,
        "pythonVersion": platform.python_version(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "commands": command_matrix,
        "paths": path_matrix,
        "missingPaths": missing_paths,
        "missingCommands": missing_commands,
        "toolchainHash": hash_directory(repo_root / "tools/hos", ignore_dirs={".git", "__pycache__"}),
    }

    report_name = f"doctor_{timestamp_slug()}.json"
    report = write_json_report(
        repo_root=repo_root,
        file_name=report_name,
        payload=payload,
        local=True,
        subdir="doctor",
    )

    if args.json:
        print(dump_json(payload), end="")
    else:
        print(
            f"[doctor] ok={payload['ok']} python={payload['pythonVersion']} "
            f"missingPaths={len(missing_paths)} missingCommands={len(missing_commands)}"
        )
        print(f"[doctor] report={report.as_posix()}")
        if missing_paths:
            for path in missing_paths:
                print(f" - missing path: {path}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
