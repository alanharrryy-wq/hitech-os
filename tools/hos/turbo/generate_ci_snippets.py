#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.stable_json import load_json
from tools.hos._core.stable_text import write_text

PROFILES_PATH = Path("tools/hos/turbo/profiles.json")


def build_remote_cache_doc() -> str:
    return """# REMOTE_CACHE_SETUP

Turbo remote cache integration is available but **OFF by default** for this repository.
Enable it explicitly in your CI pipeline when constitution/governance allows activation.

## Required Secret Names

- `TURBO_TOKEN`
- `TURBO_TEAM`
- Optional: `TURBO_API`

Only secret names are documented here. Never commit secret values.

## GitHub Actions Example (Optional)

```yaml
name: ci
on: [push, pull_request]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: pnpm install --frozen-lockfile
      - name: Optional Turbo remote cache env
        run: echo "Remote cache vars ready"
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
          TURBO_TEAM: ${{ secrets.TURBO_TEAM }}
          TURBO_API: ${{ secrets.TURBO_API }}
      - run: python tools/hos/turbo/turbo_wrap.py --ci --profile stable -- run build
```

## Generic CI Example (Optional)

1. Provide secret env names `TURBO_TOKEN` and `TURBO_TEAM`.
2. Optionally provide `TURBO_API` for custom endpoint.
3. Run:

```powershell
python tools/hos/turbo/remote_cache_check.py --require
python tools/hos/turbo/turbo_wrap.py --ci --profile stable -- run build
```

## Local Usage (No hard-fail)

```powershell
python tools/hos/turbo/remote_cache_check.py
python tools/hos/turbo/turbo_wrap.py --profile balanced -- run lint
```

Local mode continues without remote cache variables and only emits warnings.
"""


def build_profiles_doc(repo_root: Path) -> str:
    payload = load_json(repo_root / PROFILES_PATH)
    profiles = payload.get("profiles", {}) if isinstance(payload, dict) else {}
    lines: list[str] = []
    lines.append("# TURBO_PROFILES")
    lines.append("")
    lines.append("Execution profiles are available but **OFF by default** until constitution enables policy.")
    lines.append("")
    lines.append("| Profile | Concurrency | Intended For |")
    lines.append("|---|---:|---|")
    for name in sorted(profiles):
        profile = profiles[name]
        if not isinstance(profile, dict):
            continue
        concurrency = profile.get("concurrency", "n/a")
        intended_for = str(profile.get("intendedFor", ""))
        lines.append(f"| `{name}` | `{concurrency}` | {intended_for} |")
    lines.append("")
    lines.append("## Resolver")
    lines.append("")
    lines.append("```powershell")
    lines.append("python tools/hos/turbo/resolve_profile.py")
    lines.append("python tools/hos/turbo/resolve_profile.py --profile stable --json")
    lines.append("```")
    lines.append("")
    lines.append("## Wrapper")
    lines.append("")
    lines.append("```powershell")
    lines.append("python tools/hos/turbo/turbo_wrap.py --profile stable -- run build")
    lines.append("python tools/hos/turbo/turbo_wrap.py --ci --profile stable -- run test")
    lines.append("```")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    repo_root = find_repo_root()
    remote_doc = build_remote_cache_doc()
    profiles_doc = build_profiles_doc(repo_root=repo_root)

    remote_path = repo_root / "docs/system/REMOTE_CACHE_SETUP.md"
    profiles_path = repo_root / "docs/system/TURBO_PROFILES.md"
    write_text(remote_path, remote_doc, trailing_newline=True)
    write_text(profiles_path, profiles_doc, trailing_newline=True)
    print(f"[generate_ci_snippets] wrote {remote_path.as_posix()} and {profiles_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
