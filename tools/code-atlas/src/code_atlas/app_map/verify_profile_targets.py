from __future__ import annotations
import json
import sys
from pathlib import Path

THIS = Path(__file__).resolve()
SRC = THIS.parents[2]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from code_atlas.app_map.profile_targets import app_target_summary


def main() -> int:
    summary = app_target_summary()
    if "targets" not in summary:
        raise SystemExit("missing targets key")
    print(json.dumps({"status": "PASS_PROFILE_TARGETS_IMPORTABLE", **summary}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
