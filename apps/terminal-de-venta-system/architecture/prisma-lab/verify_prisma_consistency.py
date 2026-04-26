#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve()
TERMINAL_ROOT = HERE.parents[2]
CANONICAL_VALIDATOR = TERMINAL_ROOT / "tooling" / "scripts" / "validate_prisma_canonical.py"


def main() -> int:
    return subprocess.run([sys.executable, str(CANONICAL_VALIDATOR), *sys.argv[1:]], text=True).returncode


if __name__ == "__main__":
    raise SystemExit(main())
