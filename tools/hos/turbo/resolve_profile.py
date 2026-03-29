#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.stable_json import load_json

PROFILES_FILE = "tools/hos/turbo/profiles.json"
PROFILE_ENV = "HOS_TURBO_PROFILE"
VALID_PROFILE_NAMES = ("stable", "balanced", "aggressive")


@dataclass(frozen=True)
class ProfileResolution:
    profile: str
    concurrency: int | str
    source: str
    logical_cores: int
    reason: str


def load_profiles(repo_root: Path) -> dict[str, dict[str, Any]]:
    path = repo_root / PROFILES_FILE
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"invalid profile file: {path}")
    profiles = payload.get("profiles", {})
    if not isinstance(profiles, dict):
        raise ValueError(f"invalid profile structure: {path}")
    normalized: dict[str, dict[str, Any]] = {}
    for name in sorted(profiles):
        if name not in VALID_PROFILE_NAMES:
            continue
        config = profiles[name]
        if not isinstance(config, dict):
            continue
        concurrency = config.get("concurrency")
        if isinstance(concurrency, int) and concurrency > 0:
            value: int | str = concurrency
        elif isinstance(concurrency, str) and concurrency == "auto":
            value = "auto"
        else:
            continue
        normalized[name] = {"concurrency": value, "description": str(config.get("description", ""))}
    if not normalized:
        raise ValueError("no valid turbo profiles found")
    return normalized


def detect_logical_cores() -> int:
    value = os.cpu_count()
    return value if isinstance(value, int) and value > 0 else 1


def recommend_profile(logical_cores: int) -> str:
    if logical_cores <= 4:
        return "stable"
    if logical_cores <= 12:
        return "balanced"
    return "aggressive"


def resolve_profile(
    repo_root: Path,
    requested: str | None = None,
    env: dict[str, str] | None = None,
) -> ProfileResolution:
    env_map = env if env is not None else dict(os.environ)
    profiles = load_profiles(repo_root)
    logical = detect_logical_cores()
    recommended = recommend_profile(logical)

    if requested:
        normalized = requested.strip().lower()
        if normalized not in profiles:
            raise ValueError(f"unknown turbo profile: {requested}")
        source = "cli"
        chosen = normalized
        reason = "explicit CLI selection"
    elif env_map.get(PROFILE_ENV):
        normalized = env_map[PROFILE_ENV].strip().lower()
        if normalized not in profiles:
            raise ValueError(f"invalid {PROFILE_ENV} value: {env_map[PROFILE_ENV]}")
        source = "env"
        chosen = normalized
        reason = f"environment override via {PROFILE_ENV}"
    else:
        chosen = recommended
        source = "recommended"
        reason = f"based on detected logical cores ({logical})"

    return ProfileResolution(
        profile=chosen,
        concurrency=profiles[chosen]["concurrency"],
        source=source,
        logical_cores=logical,
        reason=reason,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve Turbo profile for deterministic execution.")
    parser.add_argument("--profile", choices=VALID_PROFILE_NAMES, help="Force profile from CLI.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    resolution = resolve_profile(repo_root=repo_root, requested=args.profile)
    payload = {
        "profile": resolution.profile,
        "concurrency": resolution.concurrency,
        "source": resolution.source,
        "logicalCores": resolution.logical_cores,
        "reason": resolution.reason,
    }
    if args.json:
        from tools.hos._core.stable_json import dump_json

        print(dump_json(payload), end="")
    else:
        print(
            f"[resolve_profile] profile={resolution.profile} concurrency={resolution.concurrency} "
            f"source={resolution.source} cores={resolution.logical_cores} reason={resolution.reason}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
