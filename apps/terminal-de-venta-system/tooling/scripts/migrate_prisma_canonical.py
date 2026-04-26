#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


TERMINAL_ROOT = Path(__file__).resolve().parents[2]
APPLY = TERMINAL_ROOT / "tooling" / "scripts" / "apply_prisma_migrations_sqlite.py"


def prisma_file_url(path: Path) -> str:
    return "file:" + path.resolve().as_posix()


def main() -> int:
    env = dict(os.environ)
    env.setdefault(
        "DATABASE_URL",
        prisma_file_url(TERMINAL_ROOT.parents[1] / "tools" / "_local" / "data" / "terminal-de-venta-system" / "canonical.db"),
    )
    return subprocess.run([sys.executable, str(APPLY)], env=env, text=True).returncode


if __name__ == "__main__":
    raise SystemExit(main())
