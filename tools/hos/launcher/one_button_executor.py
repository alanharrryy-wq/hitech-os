from __future__ import annotations

from pathlib import Path
import sys

if __package__ in {None, ""}:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from tools.hos.launcher.txn_runtime import main


if __name__ == "__main__":
    raise SystemExit(main())
