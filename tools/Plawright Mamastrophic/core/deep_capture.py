#!/usr/bin/env python3
"""PRISMA Plawright Mamastrophic deep-capture marker.

The actual screenshot engine lives in tests/surf8.deep-capture.cjs because
Playwright capture runs inside Node. This small Python module exists so quick
install/self-test commands can verify that the deep-capture component is present
without launching a browser or touching live dev processes.
"""

from __future__ import annotations

from pathlib import Path


def component_status(root: Path | None = None) -> dict[str, object]:
    base = root or Path(__file__).resolve().parents[1]
    js_engine = base / "tests" / "surf8.deep-capture.cjs"
    return {
        "component": "deep-capture",
        "python_marker": str(Path(__file__).resolve()),
        "node_engine": str(js_engine),
        "node_engine_exists": js_engine.exists(),
        "status": "PASS" if js_engine.exists() else "FAIL",
    }


def main() -> int:
    status = component_status()
    print(status)
    return 0 if status["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
