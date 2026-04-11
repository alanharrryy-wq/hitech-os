#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capatch_runtime.readiness_gate import run_readiness_gate


def main(argv: list[str] | None = None) -> int:
    payload = run_readiness_gate(ROOT, ROOT / "reports" / "telemetry")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["status"] == "promotable" else 1


if __name__ == "__main__":
    raise SystemExit(main())
