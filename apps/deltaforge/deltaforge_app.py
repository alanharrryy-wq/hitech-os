from __future__ import annotations

import sys
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    # Keep local app packages (application/bootstrap/domain/...) importable from any cwd.
    sys.path.insert(0, str(APP_ROOT))

from bootstrap import run


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
