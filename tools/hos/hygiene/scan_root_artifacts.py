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
from tools.hos._core.stable_json import dump_json

ROOT_FILE_PATTERNS: tuple[str, ...] = (
    "*.log",
    "*.tmp",
    "*.temp",
    "*.bak",
    "*.orig",
    "*.rej",
    "*.cache",
    "*.swp",
)

IGNORED_ROOT_FILES: set[str] = {
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    "README.md",
    "SECURITY.md",
    "KERNEL_CONTEXT.md",
    "eslint.config.mjs",
    "prettier.config.cjs",
    "package.json",
    "pnpm-lock.yaml",
    "pnpm-workspace.yaml",
    "turbo.json",
    "tsconfig.json",
}


def scan_root_artifacts(repo_root: Path) -> dict[str, Any]:
    root_entries = sorted(repo_root.iterdir(), key=lambda item: item.name.lower())
    suspicious_files: list[str] = []
    suspicious_dirs: list[str] = []

    for entry in root_entries:
        name = entry.name
        if entry.is_file():
            if name in IGNORED_ROOT_FILES:
                continue
            if any(entry.match(pattern) for pattern in ROOT_FILE_PATTERNS):
                suspicious_files.append(name)
                continue
            if name.startswith("tmp") or name.startswith("debug"):
                suspicious_files.append(name)
        elif entry.is_dir():
            if name.startswith("tmp") or name.startswith("scratch") or name.startswith("debug"):
                suspicious_dirs.append(name)

    return {
        "root": repo_root.as_posix(),
        "suspiciousFileCount": len(suspicious_files),
        "suspiciousDirCount": len(suspicious_dirs),
        "suspiciousFiles": suspicious_files,
        "suspiciousDirs": suspicious_dirs,
        "ok": len(suspicious_files) == 0 and len(suspicious_dirs) == 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan root directory for junk artifacts.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    payload = scan_root_artifacts(repo_root=repo_root)
    if args.json:
        print(dump_json(payload), end="")
    else:
        print(
            f"[scan_root_artifacts] ok={payload['ok']} suspiciousFiles={payload['suspiciousFileCount']} "
            f"suspiciousDirs={payload['suspiciousDirCount']}"
        )
        for name in payload["suspiciousFiles"]:
            print(f" - file: {name}")
        for name in payload["suspiciousDirs"]:
            print(f" - dir: {name}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
