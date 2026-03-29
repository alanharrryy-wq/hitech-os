#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
import os
from dataclasses import dataclass
from pathlib import Path

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.stable_json import dump_json

REQUIRED_ENV_VARS: tuple[str, ...] = ("TURBO_TOKEN", "TURBO_TEAM")
OPTIONAL_ENV_VARS: tuple[str, ...] = ("TURBO_API",)


@dataclass(frozen=True)
class RemoteCacheStatus:
    required_present: tuple[str, ...]
    required_missing: tuple[str, ...]
    optional_present: tuple[str, ...]
    optional_missing: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return len(self.required_missing) == 0


def evaluate_remote_cache_env(env: dict[str, str] | None = None) -> RemoteCacheStatus:
    mapping = env if env is not None else dict(os.environ)
    required_present = tuple(sorted(name for name in REQUIRED_ENV_VARS if mapping.get(name)))
    required_missing = tuple(sorted(name for name in REQUIRED_ENV_VARS if not mapping.get(name)))
    optional_present = tuple(sorted(name for name in OPTIONAL_ENV_VARS if mapping.get(name)))
    optional_missing = tuple(sorted(name for name in OPTIONAL_ENV_VARS if not mapping.get(name)))

    return RemoteCacheStatus(
        required_present=required_present,
        required_missing=required_missing,
        optional_present=optional_present,
        optional_missing=optional_missing,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check Turbo remote cache environment variable presence. "
            "This command never prints secret values."
        )
    )
    parser.add_argument("--require", action="store_true", help="Return non-zero when required vars are missing.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status = evaluate_remote_cache_env()
    payload = {
        "ok": status.ok,
        "requiredPresent": list(status.required_present),
        "requiredMissing": list(status.required_missing),
        "optionalPresent": list(status.optional_present),
        "optionalMissing": list(status.optional_missing),
    }

    if args.json:
        print(dump_json(payload), end="")
    else:
        state = "PASS" if status.ok else "WARN"
        print(
            f"[remote_cache_check] {state} required_present={len(status.required_present)} "
            f"required_missing={len(status.required_missing)}"
        )
        if status.required_missing:
            print("Missing required env names:")
            for name in status.required_missing:
                print(f" - {name}")
        if status.optional_missing:
            print("Missing optional env names:")
            for name in status.optional_missing:
                print(f" - {name}")
    if args.require and not status.ok:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
