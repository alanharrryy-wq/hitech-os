#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


TERMINAL_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = TERMINAL_ROOT / "prisma" / "schema.prisma"
APPS = {
    "pc": TERMINAL_ROOT / "products" / "pc" / "app",
    "tablet": TERMINAL_ROOT / "products" / "tablet" / "app",
}


def prisma_file_url(path: Path) -> str:
    return "file:" + path.resolve().as_posix()


def env_for(app_root: Path) -> dict[str, str]:
    env = dict(os.environ)
    env.setdefault(
        "DATABASE_URL",
        prisma_file_url(TERMINAL_ROOT.parents[1] / "tools" / "_local" / "data" / "terminal-de-venta-system" / "canonical.db"),
    )
    return env


def schema_for(app_root: Path) -> Path:
    cache = app_root / "node_modules" / ".cache" / "hitech-prisma-canonical"
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / "schema.prisma"
    target.write_text(SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    selected = APPS.items() if target == "all" else [(target, APPS[target])]
    pnpm = shutil.which("pnpm") or shutil.which("pnpm.cmd")
    if not pnpm:
        print("pnpm executable not found", file=sys.stderr)
        return 127
    for name, app_root in selected:
        schema = schema_for(app_root)
        result = subprocess.run(
            [pnpm, "exec", "prisma", "generate", "--schema", str(schema)],
            cwd=str(app_root),
            env=env_for(app_root),
            text=True,
        )
        if result.returncode != 0:
            print(f"canonical Prisma generate failed for {name}", file=sys.stderr)
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
