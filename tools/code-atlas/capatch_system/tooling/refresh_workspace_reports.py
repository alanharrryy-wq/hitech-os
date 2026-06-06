#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capatch_audit.telemetry import refresh_existing_telemetry


def main(argv: list[str] | None = None) -> int:
    root_dir = ROOT
    if argv:
        root_dir = Path(argv[0]).expanduser().resolve()
    actions = refresh_existing_telemetry(root_dir)
    payload = {
        "name": "refresh_workspace_reports",
        "root_dir": str(root_dir),
        "updated": sum(1 for item in actions if item.get("status") == "updated"),
        "unchanged": sum(1 for item in actions if item.get("status") == "unchanged"),
        "actions": actions,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
