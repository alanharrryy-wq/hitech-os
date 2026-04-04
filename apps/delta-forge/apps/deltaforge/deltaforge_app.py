from __future__ import annotations

import sys
from pathlib import Path


ENTRYPOINT = Path(__file__).resolve()
APP_ROOT = ENTRYPOINT.parent
RUNNABLE_ROOT = ENTRYPOINT.parents[2]

for path in (RUNNABLE_ROOT, APP_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        # Keep local app packages and forgeos shared modules importable from any cwd.
        sys.path.insert(0, path_str)

from bootstrap import run


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
